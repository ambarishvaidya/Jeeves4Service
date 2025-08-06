from unittest.mock import Mock
from sqlalchemy.orm import Session

from services.property_service.app.dto.storage import PropertyStorageResponse
from services.property_service.app.services.get_storage import GetStorage


class TestGetStorage:

    def setup_method(self):
        self.mock_logger = Mock()
        self.mock_session = Mock(spec=Session)
        self.service = GetStorage(self.mock_logger, self.mock_session)

    def test_get_storage_by_property_success(self):
        property_id = 1
        mock_storage = [
            Mock(id=1, property_id=1, room_id=1, container_id=None, storage_name="Main Wardrobe"),
            Mock(id=2, property_id=1, room_id=1, container_id=1, storage_name="Top Shelf")
        ]
        self.mock_session.query.return_value.filter.return_value.all.return_value = mock_storage

        result = self.service.get_storage_by_property(property_id)

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].property_id == 1
        assert result[0].room_id == 1
        assert result[0].container_id is None
        assert result[0].storage_name == "Main Wardrobe"
        assert result[1].id == 2
        assert result[1].container_id == 1
        assert result[1].storage_name == "Top Shelf"

    def test_get_storage_by_property_empty(self):
        property_id = 999
        self.mock_session.query.return_value.filter.return_value.all.return_value = []

        result = self.service.get_storage_by_property(property_id)

        assert len(result) == 0

    def test_get_storage_by_room_success(self):
        room_id = 1
        mock_storage = [
            Mock(id=1, property_id=1, room_id=1, container_id=None, storage_name="Main Wardrobe"),
            Mock(id=2, property_id=1, room_id=1, container_id=1, storage_name="Top Shelf")
        ]
        self.mock_session.query.return_value.filter.return_value.all.return_value = mock_storage

        result = self.service.get_storage_by_room(room_id)

        assert len(result) == 2
        assert result[0].room_id == 1
        assert result[0].storage_name == "Main Wardrobe"
        assert result[1].room_id == 1
        assert result[1].storage_name == "Top Shelf"

    def test_get_storage_by_room_empty(self):
        room_id = 999
        self.mock_session.query.return_value.filter.return_value.all.return_value = []

        result = self.service.get_storage_by_room(room_id)

        assert len(result) == 0

    def test_get_storage_by_id_success(self):
        storage_id = 1
        mock_storage = Mock(id=1, property_id=1, room_id=1, container_id=None, storage_name="Main Wardrobe")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_storage

        result = self.service.get_storage_by_id(storage_id)

        assert result is not None
        assert result.id == 1
        assert result.property_id == 1
        assert result.room_id == 1
        assert result.container_id is None
        assert result.storage_name == "Main Wardrobe"

    def test_get_storage_by_id_not_found(self):
        storage_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        result = self.service.get_storage_by_id(storage_id)

        assert result is None

    def test_get_storage_by_property_exception(self):
        property_id = 1
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_storage_by_property(property_id)

        assert len(result) == 0
        self.mock_logger.error.assert_called_once()

    def test_get_storage_by_id_exception(self):
        storage_id = 1
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_storage_by_id(storage_id)

        assert result is None
        self.mock_logger.error.assert_called_once()
