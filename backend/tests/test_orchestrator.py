"""
Unit tests for HackTheAgent multi-agent orchestrator
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.orchestrator import (
    MultiAgentOrchestrator,
    WorkflowStatus,
    WorkflowStep,
    WorkflowExecution,
    get_orchestrator
)


class TestWorkflowStep:
    """Test WorkflowStep dataclass"""
    
    def test_workflow_step_creation(self):
        """Test creating a workflow step"""
        step = WorkflowStep(
            step_id="test_step",
            agent="Test Agent",
            description="Test description"
        )
        
        assert step.step_id == "test_step"
        assert step.agent == "Test Agent"
        assert step.status == WorkflowStatus.PENDING
        assert step.result is None
        assert step.error is None
    
    def test_workflow_step_to_dict(self):
        """Test converting workflow step to dictionary"""
        step = WorkflowStep(
            step_id="test_step",
            agent="Test Agent",
            description="Test description",
            status=WorkflowStatus.COMPLETED,
            result="Test result"
        )
        
        step_dict = step.to_dict()
        
        assert step_dict['step_id'] == "test_step"
        assert step_dict['agent'] == "Test Agent"
        assert step_dict['status'] == "completed"  # Should be string, not enum
        assert step_dict['result'] == "Test result"


class TestWorkflowExecution:
    """Test WorkflowExecution dataclass"""
    
    def test_workflow_execution_creation(self):
        """Test creating a workflow execution"""
        execution = WorkflowExecution(
            execution_id="exec_1",
            intent="Find emails about meetings"
        )
        
        assert execution.execution_id == "exec_1"
        assert execution.intent == "Find emails about meetings"
        assert execution.status == WorkflowStatus.PENDING
        assert len(execution.steps) == 0
    
    def test_workflow_execution_to_dict(self):
        """Test converting execution to dictionary"""
        step = WorkflowStep(
            step_id="step_1",
            agent="Intent Agent",
            description="Analyze intent"
        )
        
        execution = WorkflowExecution(
            execution_id="exec_1",
            intent="Test query",
            steps=[step]
        )
        
        exec_dict = execution.to_dict()
        
        assert exec_dict['execution_id'] == "exec_1"
        assert exec_dict['intent'] == "Test query"
        assert len(exec_dict['steps']) == 1
        assert exec_dict['steps'][0]['step_id'] == "step_1"


class TestMultiAgentOrchestrator:
    """Test MultiAgentOrchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a fresh orchestrator for each test"""
        return MultiAgentOrchestrator()
    
    @pytest.mark.asyncio
    async def test_intent_detection_step(self, orchestrator):
        """Test intent detection step"""
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="Find emails about meetings"
        )
        
        step = await orchestrator._step_intent_detection(execution, "Find emails about meetings")
        
        assert step.step_id == "step_1_intent"
        assert step.agent == "Intent Detection Agent"
        assert step.status == WorkflowStatus.COMPLETED
        assert step.metadata['intent_type'] in ['search', 'summarization', 'analysis', 'sender_analysis', 'temporal_search']
        assert step.result is not None
    
    @pytest.mark.asyncio
    async def test_intent_detection_summarize(self, orchestrator):
        """Test intent detection for summarization query"""
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="Summarize my emails"
        )
        
        step = await orchestrator._step_intent_detection(execution, "Summarize my emails")
        
        assert step.metadata['intent_type'] == 'summarization'
    
    @pytest.mark.asyncio
    async def test_intent_detection_analysis(self, orchestrator):
        """Test intent detection for analysis query"""
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="How many emails did I get?"
        )
        
        step = await orchestrator._step_intent_detection(execution, "How many emails did I get?")
        
        assert step.metadata['intent_type'] == 'analysis'
    
    @pytest.mark.asyncio
    @patch('app.orchestrator.get_search_engine')
    async def test_semantic_search_step_success(self, mock_search, orchestrator):
        """Test semantic search step with successful search"""
        # Mock search engine
        mock_engine = MagicMock()
        mock_engine.search.return_value = [
            {'id': '1', 'subject': 'Meeting notes', 'from': 'alice@example.com', 'score': 0.95},
            {'id': '2', 'subject': 'Team sync', 'from': 'bob@example.com', 'score': 0.87}
        ]
        mock_search.return_value = mock_engine
        
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="Find meetings"
        )
        
        step = await orchestrator._step_semantic_search(execution, "Find meetings", top_k=5)
        
        assert step.step_id == "step_2_search"
        assert step.agent == "Semantic Search Agent"
        assert step.status == WorkflowStatus.COMPLETED
        assert step.metadata['result_count'] == 2
        assert len(step.metadata['results']) == 2
    
    @pytest.mark.asyncio
    @patch('app.orchestrator.get_search_engine')
    async def test_semantic_search_step_no_results(self, mock_search, orchestrator):
        """Test semantic search step with no results"""
        mock_engine = MagicMock()
        mock_engine.search.return_value = []
        mock_search.return_value = mock_engine
        
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="Find nonexistent emails"
        )
        
        step = await orchestrator._step_semantic_search(execution, "Find nonexistent", top_k=5)
        
        assert step.status == WorkflowStatus.COMPLETED
        assert step.metadata['result_count'] == 0
    
    @pytest.mark.asyncio
    @patch('app.orchestrator.get_search_engine')
    async def test_semantic_search_step_error(self, mock_search, orchestrator):
        """Test semantic search step with error"""
        mock_engine = MagicMock()
        mock_engine.search.side_effect = Exception("Search failed")
        mock_search.return_value = mock_engine
        
        execution = WorkflowExecution(
            execution_id="test_1",
            intent="Find emails"
        )
        
        step = await orchestrator._step_semantic_search(execution, "Find emails", top_k=5)
        
        assert step.status == WorkflowStatus.ERROR
        assert step.error is not None
    
    def test_orchestrator_get_execution(self, orchestrator):
        """Test retrieving execution by ID"""
        execution = WorkflowExecution(execution_id="exec_1", intent="Test")
        orchestrator.executions["exec_1"] = execution
        
        retrieved = orchestrator.get_execution("exec_1")
        
        assert retrieved is not None
        assert retrieved.execution_id == "exec_1"
    
    def test_orchestrator_get_execution_not_found(self, orchestrator):
        """Test retrieving non-existent execution"""
        retrieved = orchestrator.get_execution("nonexistent")
        
        assert retrieved is None
    
    def test_orchestrator_list_recent_executions(self, orchestrator):
        """Test listing recent executions"""
        # Add some executions with different timestamps
        for i in range(5):
            execution = WorkflowExecution(execution_id=f"exec_{i}", intent=f"Test {i}")
            orchestrator.executions[f"exec_{i}"] = execution
        
        recent = orchestrator.list_recent_executions(limit=3)
        
        assert len(recent) == 3
    
    def test_get_orchestrator_singleton(self):
        """Test that get_orchestrator returns the same instance"""
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        
        assert orch1 is orch2


class TestIntentDetection:
    """Test intent detection logic"""
    
    @pytest.mark.asyncio
    async def test_intent_variations(self):
        """Test various intent queries"""
        orchestrator = MultiAgentOrchestrator()
        
        test_cases = [
            ("summarize my emails", "summarization"),
            ("what are my recent emails", "summarization"),
            ("count the emails from john", "analysis"),
            ("how many emails today", "analysis"),
            ("when did alice email me", "temporal_search"),
            ("find emails from bob", "sender_analysis"),
            ("search for meeting notes", "search"),
            ("find urgent emails", "search")
        ]
        
        for query, expected_intent in test_cases:
            execution = WorkflowExecution(execution_id="test", intent=query)
            step = await orchestrator._step_intent_detection(execution, query)
            assert step.metadata['intent_type'] == expected_intent, f"Query '{query}' failed"


class TestWorkflowStatusEnum:
    """Test WorkflowStatus enum"""
    
    def test_workflow_status_values(self):
        """Test WorkflowStatus enum values"""
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.ERROR.value == "error"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
