# Sprint 0 – Product Vision & Product Backlog

## Product Vision

> For small community and school libraries that still track their stock on paper,
> **Library Inventory** is a lightweight command-line application that lets a librarian
> catalogue books, e-books and audiobooks, lend them to borrowers and instantly see what is
> available — with every record safely persisted to a JSON file.

## Users / Personas

| Persona | Need |
|---|---|
| **Librarian** (primary user) | Catalogue items, lend and receive them back, answer "do we have…?" questions quickly |
| **Library manager** | Get simple reports on stock and lending activity |
| **Maintainer (developer/ops)** | Know the application is healthy and diagnose problems from logs |

## Product Backlog

| ID | User Story |
|---|---|
| US-01 | As a **librarian**, I want to add a book with its author(s), ISBN, genre and year so that the item is catalogued in the inventory. |
| US-02 | As a **librarian**, I want to search books by title or author so that I can quickly tell a visitor whether we hold a book. |
| US-03 | As a **librarian**, I want the inventory to be saved to and loaded from a JSON file so that no data is lost when the application is closed. |
| US-04 | As a **librarian**, I want to register borrowers and lend an available book to them so that I know who has which item. |
| US-05 | As a **librarian**, I want to record the return of a borrowed book and keep a borrowing history so that items become available again and past loans can be audited. |
| US-06 | As a **librarian**, I want to catalogue e-books and audiobooks with their specific details (file format/size, narrator/duration) so that digital items are managed alongside print books. |
| US-07 | As a **library manager**, I want reports of available books, borrowed books and books grouped by author so that I can understand the state of the collection. |
| US-08 | As a **maintainer**, I want a health check and application logs so that I can verify the system is working and troubleshoot errors. |
| US-09 | As a **librarian**, I want to update or remove a book record so that the catalogue stays accurate. |
| US-10 | As a **librarian**, I want loans to have a due date and see overdue items so that I can chase late returns. |
