import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


def test_page_shows_task_list_and_form(page: Page):
    """REQ-011: The page shows the list of tasks with their title, due date and status, and a form to add a task."""
    page.goto(BASE_URL + "/")
    page.wait_for_load_state("networkidle")
    # Check form elements exist
    expect(page.locator("#add-form")).to_be_visible()
    expect(page.locator("#title-input")).to_be_visible()
    expect(page.locator("#due-date-input")).to_be_visible()
    expect(page.locator("#add-form button[type='submit']")).to_be_visible()
    # Initially the list may be empty, but container must exist
    expect(page.locator("#task-list")).to_be_visible()


def test_add_task_and_see_in_list(page: Page):
    """Add a task via form and verify it appears in the list with title, due date, status."""
    page.goto(BASE_URL + "/")
    page.wait_for_load_state("networkidle")
    page.fill("#title-input", "Test from Playwright")
    page.fill("#due-date-input", "2025-06-15")
    page.click("#add-form button[type='submit']")
    # Wait for the list to update
    page.wait_for_selector("#task-list li:has-text('Test from Playwright')", timeout=5000)
    expect(page.locator("#task-list")).to_contain_text("2025-06-15")
    expect(page.locator("#task-list")).to_contain_text("open")


def test_done_and_delete_buttons(page: Page):
    """REQ-012: Each open task has a Done button that completes it, and each task has a Delete button."""
    page.goto(BASE_URL + "/")
    page.wait_for_load_state("networkidle")
    # Create a task
    page.fill("#title-input", "Task for done/delete test")
    page.click("#add-form button[type='submit']")
    # Wait for task to appear
    page.wait_for_selector("#task-list li:has-text('Task for done/delete test')", timeout=5000)
    # Check Done button is present for open task
    done_btn = page.locator("#task-list li:has-text('Task for done/delete test') button:has-text('Done')")
    expect(done_btn).to_be_visible()
    # Check Delete button is present
    delete_btn = page.locator("#task-list li:has-text('Task for done/delete test') button:has-text('Delete')")
    expect(delete_btn).to_be_visible()


def test_done_button_completes_task(page: Page):
    """Clicking Done changes status to done and removes Done button."""
    page.goto(BASE_URL + "/")
    page.wait_for_load_state("networkidle")
    page.fill("#title-input", "To be completed")
    page.click("#add-form button[type='submit']")
    # Wait for task to appear in list
    page.wait_for_selector("#task-list li:has-text('To be completed')", timeout=5000)
    # Click Done
    page.click("#task-list li:has-text('To be completed') button:has-text('Done')")
    # Wait for status to become done
    page.wait_for_selector("#task-list li:has-text('done')", timeout=5000)
    # The Done button should be gone
    expect(page.locator("#task-list li:has-text('To be completed') button:has-text('Done')")).to_have_count(0)


def test_delete_button_removes_task(page: Page):
    """Clicking Delete removes the task from the list."""
    page.goto(BASE_URL + "/")
    page.wait_for_load_state("networkidle")
    page.fill("#title-input", "Task to delete")
    page.click("#add-form button[type='submit']")
    # Wait for task to appear in list
    page.wait_for_selector("#task-list li:has-text('Task to delete')", timeout=5000)
    # Click Delete
    page.click("#task-list li:has-text('Task to delete') button:has-text('Delete')")
    # Wait for deletion
    page.wait_for_selector("#task-list li:has-text('Task to delete')", state="detached", timeout=5000)


def test_api_error_shown_next_to_form(page: Page):
    """REQ-013: When the API rejects a new task, the page shows the API's message next to the form and keeps what was typed."""
    page.goto(BASE_URL + "/")
    # Submit an empty title (will be rejected)
    page.fill("#title-input", "   ")  # Spaces only, will be trimmed to empty and rejected
    page.fill("#due-date-input", "")  # clear date
    # Wait for page to fully load (loadTasks may finish after initial render)
    page.wait_for_load_state("networkidle")
    page.click("#add-form button[type='submit']")
    # The error should appear in the #error div (after async response)
    page.wait_for_selector("#error:not(:empty)", timeout=5000)
    # The input should still contain what was typed (spaces)
    expect(page.locator("#title-input")).to_have_value("   ")
