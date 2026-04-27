import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.questionnaire_repository import QuestionnaireRepository


class TestQuestionnaireRepository:
    """Test suite for QuestionnaireRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return QuestionnaireRepository(mock_db_session)

    def create_mock_user_form(self, id=1, user_id=1, tag="Sport", detail="Football", type_tag=1):
        mock = MagicMock()
        mock.id = id
        mock.user_id = user_id
        mock.tag = tag
        mock.detail = detail
        mock.type_tag = type_tag
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    def create_mock_tag_form(self, id=1, tag_value="Sport", type_tags=True):
        mock = MagicMock()
        mock.id = id
        mock.tag_value = tag_value
        mock.type_tags = type_tags
        return mock

    @pytest.mark.asyncio
    async def test_get_user_questionnaire_success(self, repo, mock_db_session):
        mock_forms = [self.create_mock_user_form(1), self.create_mock_user_form(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_forms)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_questinnaire(1)

        assert len(result) == 2
        assert result == mock_forms

    @pytest.mark.asyncio
    async def test_get_user_questionnaire_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_questinnaire(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_standart_tags_success(self, repo, mock_db_session):
        mock_tags = [self.create_mock_tag_form(1, "Sport"), self.create_mock_tag_form(2, "Music")]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_tags)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_standart_tags(1, is_interest=True)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_standart_tags_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_standart_tags(1, is_interest=False)

        assert result == []

    @pytest.mark.asyncio
    async def test_delete_user_questionnaire_success(self, repo, mock_db_session):
        mock_db_session.execute = AsyncMock()
        mock_db_session.commit = AsyncMock()

        await repo.delete_user_questionnaire(1)

        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_questionnaire_with_interests_only(self, repo, mock_db_session):
        interests = [{"tag": "Sport", "details": "Football"}, {"tag": "Music", "details": "Rock"}]
        avoid_gifts = []

        mock_db_session.add_all = MagicMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.create_questionnaire(1, interests, avoid_gifts)

        assert len(result) == 2
        mock_db_session.add_all.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_questionnaire_with_avoid_only(self, repo, mock_db_session):
        interests = []
        avoid_gifts = [{"tag": "Sweets", "details": "Chocolate"}]

        mock_db_session.add_all = MagicMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.create_questionnaire(1, interests, avoid_gifts)

        assert len(result) == 1
        mock_db_session.add_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_questionnaire_with_both(self, repo, mock_db_session):
        interests = [{"tag": "Sport", "details": "Football"}]
        avoid_gifts = [{"tag": "Sweets", "details": "Chocolate"}]

        mock_db_session.add_all = MagicMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.create_questionnaire(1, interests, avoid_gifts)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_create_questionnaire_empty(self, repo, mock_db_session):
        interests = []
        avoid_gifts = []

        result = await repo.create_questionnaire(1, interests, avoid_gifts)

        assert result == []
        mock_db_session.add_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_tag_success(self, repo, mock_db_session):
        mock_tag = self.create_mock_tag_form(1, "Sport")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_tag)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_tag("Sport", True)

        assert result == mock_tag

    @pytest.mark.asyncio
    async def test_get_tag_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_tag("NonExistent", True)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_tag_user_success(self, repo, mock_db_session):
        mock_form = self.create_mock_user_form(1, 1, "Sport")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_form)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_tag_user(1, "Sport", True)

        assert result == mock_form

    @pytest.mark.asyncio
    async def test_get_tag_user_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_tag_user(1, "NonExistent", True)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_tag_success(self, repo, mock_db_session):
        mock_form = self.create_mock_user_form(1, 1, "NewTag", "Detail", True)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.questionnaire_repository.UserForm', return_value=mock_form):
            result = await repo.create_tag(1, "NewTag", "Detail", True)

            assert result == mock_form
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()