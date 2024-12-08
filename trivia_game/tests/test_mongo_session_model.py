import pytest

from models.mongo_session_model import login_user, logout_user

@pytest.fixture
def sample_user_id():
    return 1  # Primary key for user


@pytest.fixture
def sample_combatants():
    return [{"meal_id": 1}, {"meal_id": 2}]  # Sample combatant data


def test_login_user_creates_session_if_not_exists(mocker, sample_user_id):
    """Test login_user creates a session with no combatants if it does not exist."""
    mock_find = mocker.patch("meal_max.clients.mongo_client.sessions_collection.find_one", return_value=None)
    mock_insert = mocker.patch("meal_max.clients.mongo_client.sessions_collection.insert_one")
    mock_battle_model = mocker.Mock()

    login_user(sample_user_id, mock_battle_model)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_insert.assert_called_once_with({"user_id": sample_user_id, "combatants": []})
    mock_battle_model.clear_combatants.assert_not_called()
    mock_battle_model.prep_combatant.assert_not_called()

def test_login_user_loads_combatants_if_session_exists(mocker, sample_user_id, sample_combatants):
    """Test login_user loads combatants if session exists."""
    mock_find = mocker.patch(
        "meal_max.clients.mongo_client.sessions_collection.find_one",
        return_value={"user_id": sample_user_id, "combatants": sample_combatants}
    )
    mock_battle_model = mocker.Mock()

    login_user(sample_user_id, mock_battle_model)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_battle_model.clear_combatants.assert_called_once()
    mock_battle_model.prep_combatant.assert_has_calls([mocker.call(combatant) for combatant in sample_combatants])

def test_logout_user_updates_combatants(mocker, sample_user_id, sample_combatants):
    """Test logout_user updates the combatants list in the session."""
    mock_update = mocker.patch("meal_max.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=1))
    mock_battle_model = mocker.Mock()
    mock_battle_model.get_combatants.return_value = sample_combatants

    logout_user(sample_user_id, mock_battle_model)

    mock_update.assert_called_once_with(
        {"user_id": sample_user_id},
        {"$set": {"combatants": sample_combatants}},
        upsert=False
    )
    mock_battle_model.clear_combatants.assert_called_once()

def test_logout_user_raises_value_error_if_no_user(mocker, sample_user_id, sample_combatants):
    """Test logout_user raises ValueError if no session document exists."""
    mock_update = mocker.patch("meal_max.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=0))
    mock_battle_model = mocker.Mock()
    mock_battle_model.get_combatants.return_value = sample_combatants

    with pytest.raises(ValueError, match=f"User with ID {sample_user_id} not found for logout."):
        logout_user(sample_user_id, mock_battle_model)

    mock_update.assert_called_once_with(
        {"user_id": sample_user_id},
        {"$set": {"combatants": sample_combatants}},
        upsert=False
    )