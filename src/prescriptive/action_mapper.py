"""
Action Mapper module for PLAF.

This module bridges the semantic gap between numerical counterfactuals (e.g., "increase clicks")
and pedagogical actions (e.g., "read file X", "do quiz Y").
"""

import sqlite3
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionMapper:
    """Maps numerical targets to specific educational resources and activities."""
    
    def __init__(self, db_path: str = "data/lms.db"):
        """Initialize with database path."""
        self.db_path = db_path
        
    def _connect(self):
        """Create database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def get_student_context(self, student_id: int) -> Dict:
        """Get basic student context (module, presentation)."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT code_module, code_presentation FROM students WHERE id_student = ?", 
                (student_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}
        finally:
            conn.close()

    def get_unvisited_resources(self, student_id: int, code_module: str, code_presentation: str, limit: int = 5) -> List[Dict]:
        """Find VLE resources the student has NOT visited yet."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            
            # Find resources in the student's module/presentation that are NOT in their activity log
            # Note: We assume 'activities' table uses 'resource_id' which maps to 'id_site' in 'vle'
            query = """
                SELECT v.id_site, v.activity_type, v.week_from, v.week_to
                FROM vle v
                WHERE v.code_module = ? 
                AND v.code_presentation = ?
                AND v.id_site NOT IN (
                    SELECT resource_id 
                    FROM activities 
                    WHERE id_student = ? AND resource_id IS NOT NULL
                )
                ORDER BY v.week_from ASC
                LIMIT ?
            """
            cursor.execute(query, (code_module, code_presentation, student_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching unvisited resources: {e}")
            return []
        finally:
            conn.close()

    def get_upcoming_assessments(self, student_id: int, code_module: str, code_presentation: str, limit: int = 3) -> List[Dict]:
        """Find assessments that are due soon and not yet submitted."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            
            # Find assessments for this module that don't have a submission record for this student
            # Note: This assumes 'assessments' table contains the schedule, and we check 'student_assessment' for submissions
            # But based on models.py, 'assessments' table seems to be student-specific (has id_student)
            # Let's check the schema in models.py again. 
            # models.py: CREATE TABLE IF NOT EXISTS assessments (id_student, id_assessment, date_submitted...)
            # So 'assessments' table in models.py is actually a merged table or student-specific table.
            
            query = """
                SELECT id_assessment, assessment_type, date_due, weight
                FROM assessments
                WHERE id_student = ?
                AND code_module = ?
                AND code_presentation = ?
                AND date_submitted IS NULL
                ORDER BY date_due ASC
                LIMIT ?
            """
            cursor.execute(query, (student_id, code_module, code_presentation, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching upcoming assessments: {e}")
            return []
        finally:
            conn.close()
            
    def get_low_score_assessments(self, student_id: int, limit: int = 3) -> List[Dict]:
        """Find assessments where the student scored low (< 50)."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            query = """
                SELECT id_assessment, assessment_type, score, weight
                FROM assessments
                WHERE id_student = ?
                AND score < 50
                AND score IS NOT NULL
                ORDER BY score ASC
                LIMIT ?
            """
            cursor.execute(query, (student_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching low score assessments: {e}")
            return []
        finally:
            conn.close()
    
    def _expand_assessment_type(self, assessment_type: str) -> str:
        """
        Expand assessment type abbreviations to full names.
        
        Based on OULAD descriptions.txt:
        - TMA = Tutor Marked Assessment
        - CMA = Computer Marked Assessment
        - Exam = Final Exam
        """
        type_map = {
            'TMA': 'Tutor Marked Assessment (TMA)',
            'CMA': 'Computer Marked Assessment (CMA)',
            'Exam': 'Final Exam'
        }
        return type_map.get(assessment_type, assessment_type)

    def map_actions(self, student_id: int, counterfactual_changes: Dict) -> Dict:
        """
        Map counterfactual changes to specific actionable items.
        
        Args:
            student_id: Student ID
            counterfactual_changes: Dictionary of feature changes from DiCE
            
        Returns:
            Dictionary containing specific resources and assessments to focus on.
        """
        context = self.get_student_context(student_id)
        if not context:
            logger.warning(f"Could not find context for student {student_id}")
            return {}
            
        code_module = context.get('code_module')
        code_presentation = context.get('code_presentation')
        
        actions = {
            'recommended_resources': [],
            'upcoming_assessments': [],
            'review_assessments': []
        }
        
        # Check if we need to increase engagement (clicks, vle interaction)
        needs_engagement = False
        for feature in counterfactual_changes:
            if any(x in feature.lower() for x in ['click', 'vle', 'activity', 'interaction']):
                needs_engagement = True
                break
        
        if needs_engagement:
            actions['recommended_resources'] = self.get_unvisited_resources(
                student_id, code_module, code_presentation
            )
            
        # Check if we need to improve score
        needs_score = False
        for feature in counterfactual_changes:
            if 'score' in feature.lower() or 'assessment' in feature.lower():
                needs_score = True
                break
                
        if needs_score:
            upcoming = self.get_upcoming_assessments(
                student_id, code_module, code_presentation
            )
            # Expand assessment types
            for assess in upcoming:
                assess['assessment_type'] = self._expand_assessment_type(assess.get('assessment_type', ''))
            actions['upcoming_assessments'] = upcoming
            
            low_score = self.get_low_score_assessments(student_id)
            # Expand assessment types
            for assess in low_score:
                assess['assessment_type'] = self._expand_assessment_type(assess.get('assessment_type', ''))
            actions['review_assessments'] = low_score
            
        return actions
