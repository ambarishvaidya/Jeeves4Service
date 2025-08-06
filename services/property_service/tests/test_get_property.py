from unittest.mock import Mock
from sqlalchemy.orm import Session

from services.property_service.app.dto.property import PropertyResponse
from services.property_service.app.services.get_property import GetProperty


class TestGetProperty:

    def setup_method(self):
        self.mock_logger = Mock()
        self.mock_session = Mock(spec=Session)

        self.service = GetProperty(self.mock_logger, self.mock_session)

    def test_get_properties_success_for_valid_user(self):
        user_id = 1
        mock_properties = [
            PropertyResponse(id=1, name="Property 1", address="Address 1"),
            PropertyResponse(id=2, name="Property 2", address="Address 2")
        ]
        self.mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = mock_properties

        result = self.service.get_properties(user_id)

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "Property 1"
        assert result[0].address == "Address 1"

    def test_get_properties_failed_for_invalid_user(self):
        user_id = -1
        
        self.mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

        result = self.service.get_properties(user_id)

        assert len(result) == 0        

    def test_get_property_by_id_success(self):
        property_id = 1
        mock_property = PropertyResponse(id=property_id, name="Property 1", address="Address 1")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_property

        result = self.service.get_property_by_id(property_id)

        assert result is not None
        assert result.id == property_id
        assert result.name == "Property 1"
        assert result.address == "Address 1"

    def test_get_property_by_id_not_found(self):
        property_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        result = self.service.get_property_by_id(property_id)

        assert result is None