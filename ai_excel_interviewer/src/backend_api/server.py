"""
ai_excel_interviewer/src/backend_api/server.py

Backend API for the AI Excel Interviewer.
- Handles adaptive interview question generation using Gemini LLM.
- Evaluates candidate answers against a dynamic rubric.
- Summarizes final interview performance.
- Uses centralized configuration for environment, API keys, and database.
"""

import os
import logging, json, re
from uuid import UUID
from typing import List, Dict, Any
import uvicorn

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import google.generativeai as genai

from shared_src.config import settings
from shared_src.db.database import get_db, init_db
from shared_src.db.models import InterviewSession, InterviewTurn

logging.basicConfig(level=settings.LOG_LEVEL.upper(),format='%(asctime)s - [BACKEND] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in config.")
genai.configure(api_key=settings.GOOGLE_API_KEY)
evaluation_model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="AI Excel Interviewer Backend")

class SessionCreate(BaseModel):
    user_id: str

class QuestionResponse(BaseModel):
    session_id: UUID
    question_number: int
    question_text: str

class AnswerEvaluationRequest(BaseModel):
    session_id: UUID
    answer: str

class EvaluationResult(BaseModel):
    session_id: UUID
    evaluation: str 
    feedback: str
    next_topic: str
    next_difficulty: str

class FinalSummary(BaseModel):
    score: str
    strengths: str
    areas_for_improvement: str
    full_transcript: List[Dict[str, Any]]

def _extract_json_from_response(text: str) -> Any:
    """
    Extracts JSON object from a text response from LLM.
    Handles markdown fences or inline JSON.
    """
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
        else:
            raise json.JSONDecodeError("No valid JSON object found", text, 0)
    return json.loads(json_str.strip())

@app.on_event("startup")
async def on_startup():
    """Initialize DB on startup."""
    logger.info("Application startup... initializing database.")
    await init_db()

# --- API Endpoints ---
@app.post("/interviews", status_code=201)
async def start_interview(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new interview session."""
    session = InterviewSession(user_id=session_in.user_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    logger.info(f"Started new interview session {session.id} for user {session.user_id}")
    return {"session_id": session.id}

@app.post("/questions/generate", response_model=QuestionResponse)
async def generate_question(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Generates the next question based on the session's current state."""
    stmt = select(InterviewSession).where(InterviewSession.id == session_id).options(selectinload(InterviewSession.turns))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    prompt = f"""
    You are an AI emulating a **Senior Data Analyst** conducting a professional Excel interview. 
    Your goal is to generate a **single, scenario-based, practical question** that tests the candidate's Excel skills.

    ### Interview Context
    - Candidate is on question number: {session.question_count + 1}
    - Current Topic Area: "{session.current_topic}"
    - Current Difficulty Level: "{session.current_difficulty}"
    - Previous questions asked in this session (for context — do not repeat): {[turn.question_text for turn in session.turns]}

    ### Rules for Question Generation
    1. The question must be Excel-specific, framed as a small real-world business scenario, **preferably from Finance, Operations, or Data Analytics contexts.**
    2. The scenario should directly test the **Current Topic Area**.
    3. Match the **Current Difficulty Level**:
    - Beginner → Single, straightforward function or concept.  
    - Intermediate → Requires combining 2+ functions or applying logic/criteria.  
    - Advanced → Multi-step, nested, or modeling-level challenge (e.g., pivot tables, dynamic ranges, automation).  
    4. Each question must be **unique and non-overlapping** with earlier ones. 
    5. The question should be **concise (max 3 sentences)** and clearly scorable (so answers can be right or wrong).  
    6. Return **ONLY the plain question text**, with no preamble or formatting.

    ### Example Style
    - Beginner (Formulas): "You run a bookstore, and Column A has book titles while Column B has the number of copies sold. What formula would you use to calculate the total books sold?"
    - Intermediate (Lookup): "You manage employee records where Column A has Employee IDs and Column M has salaries. On another sheet, you have a list of Employee IDs — how would you fetch the correct salary for each?"
    - Advanced (Pivot Tables): "You have a dataset with 'Date', 'Region', 'Product', and 'Sales Amount'. How would you create a report that shows monthly sales by product category, broken down by region?"
    """
    response = await evaluation_model.generate_content_async(prompt)
    question_text = response.text.strip()

    session.question_count += 1
    new_turn = InterviewTurn(
        session_id=session.id,
        question_number=session.question_count,
        question_text=question_text
    )
    db.add(new_turn)
    await db.commit()
    logger.info(f"Generated Q{session.question_count} for session {session.id}: {question_text[:80]}...")
    return QuestionResponse(session_id=session.id, question_number=session.question_count, question_text=question_text)

@app.post("/answers/evaluate", response_model=EvaluationResult)
async def evaluate_answer(request: AnswerEvaluationRequest, db: AsyncSession = Depends(get_db)):
    """Evaluates candidate's answer and determines next topic/difficulty."""
    stmt = select(InterviewSession).where(InterviewSession.id == request.session_id).options(selectinload(InterviewSession.turns))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session or not session.turns:
        raise HTTPException(status_code=404, detail="Session or turn not found.")

    current_turn: InterviewTurn = max(session.turns, key=lambda t: t.question_number)
    
    prompt = f"""
    You are an expert Excel Interview evaluator.
    The question asked was: "{current_turn.question_text}"
    The candidate's answer is: "{request.answer}"

    Analyze the answer and provide the following in a single JSON object:
    1.  "evaluation": A single string, either "Correct", "Partially Correct", or "Incorrect".
    2.  "feedback": A concise, one-sentence explanation for your evaluation. Be encouraging.
    3.  "next_topic": Suggest the next Excel topic. If the answer was Correct, move to a related advanced topic. If Incorrect, suggest a related fundamental topic.
    4.  "next_difficulty": Suggest the next difficulty. If Correct, suggest "Intermediate" or "Advanced". If Incorrect, suggest "Beginner".

    Return ONLY the JSON object.
    """
    try:
        response = await evaluation_model.generate_content_async(prompt)
        eval_data = _extract_json_from_response(response.text)
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=503, detail="AI evaluation service unavailable.")

    current_turn.candidate_answer = request.answer
    current_turn.evaluation_result = eval_data["evaluation"]
    current_turn.feedback_text = eval_data["feedback"]

    if eval_data["evaluation"] == "Correct":
        session.correct_count += 1

    session.current_topic = eval_data["next_topic"]
    session.current_difficulty = eval_data["next_difficulty"]
    await db.commit()

    return EvaluationResult(session_id=session.id, **eval_data)

@app.get("/interviews/{session_id}/summary", response_model=FinalSummary)
async def get_summary(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Generates a final summary report of the interview session."""
    stmt = select(InterviewSession).where(InterviewSession.id == session_id).options(selectinload(InterviewSession.turns))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    transcript = [
        {"question": t.question_text, "answer": t.candidate_answer,
         "evaluation": t.evaluation_result, "feedback": t.feedback_text}
        for t in sorted(session.turns, key=lambda t: t.question_number)
    ]
    prompt = f"""
    You are an expert career coach summarizing an Excel mock interview.

    Candidate's final score: {session.correct_count} out of {session.question_count}

    Full interview transcript:
    {json.dumps(transcript, indent=2)}

    Your task:
    - Analyze the transcript carefully.
    - Provide the following in a **single JSON object only**. Do not include any text outside the JSON.
    - Use a professional, constructive, and encouraging tone.
    - Keep each paragraph 2-3 sentences.

    JSON format:
    1. "strengths": A short paragraph highlighting what the candidate did well, including patterns of correct answers or good approaches.
    2. "areas_for_improvement": A short paragraph suggesting specific Excel topics or skills to practice.

    Return ONLY a valid JSON object with these fields.
    """
    try:
        response = await evaluation_model.generate_content_async(prompt)
        summary_data = _extract_json_from_response(response.text)
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=503, detail="AI summarization service unavailable.")

    return FinalSummary(
        score=f"{session.correct_count} / {session.question_count}",
        full_transcript=transcript,
        **summary_data
    )

def main():
    uvicorn.run("ai_excel_interviewer.src.backend_api.server:app",
                host="127.0.0.1",
                port=settings.AI_EXCEL_INTERVIEWER_INTERNAL_PORT,
                reload=True)

if __name__ == "__main__":
    main()