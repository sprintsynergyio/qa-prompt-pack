Feature: TodoMVC todo list (https://demo.playwright.dev/todomvc/)
- A user types a title in "What needs to be done?" and presses Enter to add a todo. Leading/trailing spaces are trimmed; an empty or whitespace-only title is not added.
- Each todo can be marked complete/incomplete with its checkbox; "Mark all as complete" toggles every todo.
- The footer shows "N items left" counting active todos ("1 item left" when singular).
- Filters All / Active / Completed show the matching todos; the URL hash changes (#/, #/active, #/completed).
- Double-clicking a title enters edit mode; Enter saves, Escape cancels; saving an empty title deletes the todo.
- The delete (×) button removes a todo. "Clear completed" removes all completed todos and is only shown when at least one todo is completed.
- Todos persist in localStorage across page reloads.
