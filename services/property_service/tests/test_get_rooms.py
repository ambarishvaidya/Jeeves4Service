from unittest.mock import Mock
from sqlalchemy.orm import Session

from services.property_service.app.dto.property import RoomResponse
from services.property_service.app.services.get_rooms import GetRooms


class TestGetRooms:

    def setup_method(self):
        self.mock_logger = Mock()
        self.mock_session = Mock(spec=Session)
        self.service = GetRooms(self.mock_logger, self.mock_session)

    def test_get_rooms_by_property_success(self):
        property_id = 1
        mock_rooms = [
            Mock(id=1, property_id=1, room_name="Living Room"),
            Mock(id=2, property_id=1, room_name="Bedroom")
        ]
        self.mock_session.query.return_value.filter.return_value.all.return_value = mock_rooms

        result = self.service.get_rooms_by_property(property_id)

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].property_id == 1
        assert result[0].room_name == "Living Room"
        assert result[1].id == 2
        assert result[1].property_id == 1
        assert result[1].room_name == "Bedroom"

    def test_get_rooms_by_property_empty(self):
        property_id = 999
        self.mock_session.query.return_value.filter.return_value.all.return_value = []

        result = self.service.get_rooms_by_property(property_id)

        assert len(result) == 0

    def test_get_room_by_id_success(self):
        room_id = 1
        mock_room = Mock(id=1, property_id=1, room_name="Living Room")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_room

        result = self.service.get_room_by_id(room_id)

        assert result is not None
        assert result.id == 1
        assert result.property_id == 1
        assert result.room_name == "Living Room"

    def test_get_room_by_id_not_found(self):
        room_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        result = self.service.get_room_by_id(room_id)

        assert result is None

    def test_get_rooms_by_property_exception(self):
        property_id = 1
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_rooms_by_property(property_id)

        assert len(result) == 0
        self.mock_logger.error.assert_called_once()

    def test_get_room_by_id_exception(self):
        room_id = 1
        self.mock_session.query.side_effect = Exception("Database error")

        result = self.service.get_room_by_id(room_id)

        assert result is None
        self.mock_logger.error.assert_called_once()
