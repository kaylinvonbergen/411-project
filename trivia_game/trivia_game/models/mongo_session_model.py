import logging
from typing import Any, List

from ..clients.mongo_client import sessions_collection
from ..utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, battle_model) -> None:
    """
    Load the user's combatants from MongoDB into the BattleModel's combatants list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current combatants in `battle_model` and loads
    the stored combatants from MongoDB into `battle_model`.

    If no session is found, it creates a new session document for the user
    with an empty combatants list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        battle_model (BattleModel): An instance of `BattleModel` where the user's combatants
                                    will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading combatants into BattleModel.", user_id)
        battle_model.clear_combatants()
        for combatant in session.get("combatants", []):
            logger.debug("Preparing combatant: %s", combatant)
            battle_model.prep_combatant(combatant)
        logger.info("Combatants successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty combatants list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "combatants": []})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, battle_model) -> None:
    """
    Store the current combatants from the BattleModel back into MongoDB.

    Retrieves the current combatants from `battle_model` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the combatants to MongoDB, the combatants list in `battle_model` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        battle_model (BattleModel): An instance of `BattleModel` from which the user's
                                    current combatants are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)
    combatants_data = battle_model.get_combatants()
    logger.debug("Current combatants for user ID %d: %s", user_id, combatants_data)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"combatants": combatants_data}},
        upsert=False  # Prevents creating a new document if not found
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Combatants successfully saved for user ID %d. Clearing BattleModel combatants.", user_id)
    battle_model.clear_combatants()
    logger.info("BattleModel combatants cleared for user ID %d.", user_id)