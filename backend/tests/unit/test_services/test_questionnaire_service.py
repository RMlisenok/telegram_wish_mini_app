# tests/unit/test_services/test_questionnaire_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.questionnaire_service import QuestionnaireService
from app.schemas.questionnaire import QuestionnaireCreate, TagCreate, TagItem


class TestQuestionnaireService:
    """Test suite for QuestionnaireService."""
    
    @pytest.fixture
    def questionnaire_service(self, mock_db_session) -> QuestionnaireService:
        """Create QuestionnaireService instance."""
        service = QuestionnaireService(mock_db_session)
        service.rep_questin = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_user_questionnaire_with_data(self, questionnaire_service):
        """Test getting user questionnaire with data."""
        # Arrange
        rows = [
            MagicMock(id=1, tag="Sport", detail="Football", type_tag=1),
            MagicMock(id=2, tag="Music", detail="Rock", type_tag=1),
            MagicMock(id=3, tag="Sweets", detail="Chocolate", type_tag=0),
        ]
        questionnaire_service.rep_questin.get_user_questinnaire = AsyncMock(return_value=rows)
        
        # Act
        result = await questionnaire_service.get_user_questionnaire(1)
        
        # Assert
        assert len(result["interests"]) == 2
        assert len(result["avoid_gifts"]) == 1
        assert result["interests"][0]["tag"] == "Sport"
        assert result["avoid_gifts"][0]["tag"] == "Sweets"
    
    @pytest.mark.asyncio
    async def test_get_user_questionnaire_empty(self, questionnaire_service):
        """Test getting empty questionnaire."""
        # Arrange
        questionnaire_service.rep_questin.get_user_questinnaire = AsyncMock(return_value=[])
        
        # Act
        result = await questionnaire_service.get_user_questionnaire(1)
        
        # Assert
        assert result["interests"] == []
        assert result["avoid_gifts"] == []
    
    @pytest.mark.asyncio
    async def test_get_available_tags(self, questionnaire_service):
        """Test getting available tags."""
        # Arrange
        tags = [
            MagicMock(tag_value="Sport"),
            MagicMock(tag_value="Music"),
        ]
        questionnaire_service.rep_questin.get_standart_tags = AsyncMock(return_value=tags)
        
        # Act
        result = await questionnaire_service.get_available(1, is_interest=True)
        
        # Assert
        assert len(result) == 2
        assert result[0]["tag_value"] == "Sport"
    
    @pytest.mark.asyncio
    async def test_create_questionnaire_success(self, questionnaire_service):
        """Test successfully creating questionnaire."""
        # Arrange
        data = QuestionnaireCreate(
            interests=[TagItem(tag="Sport", details="Football")],
            avoid_gifts=[TagItem(tag="Sweets", details="Chocolate")]
        )
        questionnaire_service.rep_questin.get_user_questinnaire = AsyncMock(return_value=[])
        questionnaire_service.rep_questin.create_questionnaire = AsyncMock(return_value=[MagicMock()])
        
        # Act
        result = await questionnaire_service.create_questionnaire(data, 1)
        
        # Assert
        assert result["success"] is True
        assert result["items_count"] == 1
    
    @pytest.mark.asyncio
    async def test_create_questionnaire_replace_existing(self, questionnaire_service):
        """Test replacing existing questionnaire."""
        # Arrange
        data = QuestionnaireCreate(
            interests=[TagItem(tag="Sport", details="Football")],
            avoid_gifts=[TagItem(tag="Sweets", details="Chocolate")]
        )
        questionnaire_service.rep_questin.get_user_questinnaire = AsyncMock(return_value=[MagicMock()])
        questionnaire_service.rep_questin.delete_user_questionnaire = AsyncMock(return_value=True)
        questionnaire_service.rep_questin.create_questionnaire = AsyncMock(return_value=[MagicMock()])
        
        # Act
        result = await questionnaire_service.create_questionnaire(data, 1)
        
        # Assert
        questionnaire_service.rep_questin.delete_user_questionnaire.assert_called_once_with(1)
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_create_tags_success(self, questionnaire_service):
        """Test successfully creating a tag."""
        # Arrange
        tag_data = TagCreate(tag_value="New Tag", type_tag=True, detail="Description")
        questionnaire_service.rep_questin.get_tag = AsyncMock(return_value=None)
        questionnaire_service.rep_questin.get_tag_user = AsyncMock(return_value=None)
        created_tag = MagicMock(id=1, tag="New Tag", detail="Description", type_tag=True, user_id=1)
        questionnaire_service.rep_questin.create_tag = AsyncMock(return_value=created_tag)
        
        # Act
        result = await questionnaire_service.create_tags(tag_data, 1)
        
        # Assert
        assert result is not None
        assert result.tag == "New Tag"
    
    @pytest.mark.asyncio
    async def test_create_tags_duplicate_standard(self, questionnaire_service):
        """Test creating duplicate standard tag."""
        # Arrange
        tag_data = TagCreate(tag_value="Sport", type_tag=True, detail="")
        questionnaire_service.rep_questin.get_tag = AsyncMock(return_value=MagicMock())
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await questionnaire_service.create_tags(tag_data, 1)
        assert exc_info.value.status_code == 400
        assert "tag_exist_standart" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_tags_duplicate_user(self, questionnaire_service):
        """Test creating duplicate user tag."""
        # Arrange
        tag_data = TagCreate(tag_value="My Tag", type_tag=True, detail="")
        questionnaire_service.rep_questin.get_tag = AsyncMock(return_value=None)
        questionnaire_service.rep_questin.get_tag_user = AsyncMock(return_value=MagicMock())
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await questionnaire_service.create_tags(tag_data, 1)
        assert exc_info.value.status_code == 400
        assert "tag_exist_user" in str(exc_info.value.detail)