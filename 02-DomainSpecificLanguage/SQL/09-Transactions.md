# Transactions — Notes

## What this covers
Grouping multiple statements into one all-or-nothing unit: ACID basics, BEGIN/COMMIT, ROLLBACK, and nested SAVEPOINTs.

## Key points
- **Atomicity** — a transaction's statements all succeed or none do, no partial writes.
- **Consistency** — a transaction moves the database from one valid state to another, never breaking declared constraints.
- **Isolation** — concurrent transactions don't see each other's uncommitted changes (SQLite serializes writers, one at a time).
- **Durability** — once COMMIT returns, the change survives a crash (fsync'd to disk).
- Every statement outside an explicit transaction runs in its own implicit auto-commit transaction.
- `BEGIN` starts a transaction you control; `COMMIT` makes its changes permanent.
- `ROLLBACK` discards every change made since `BEGIN`, restoring state as of the last commit.
- `SAVEPOINT name` marks a point inside a transaction you can roll back to without discarding the whole transaction; `ROLLBACK TO name` undoes just that part.

## Gotchas (the part worth revising twice)
- A multi-statement operation (like a money transfer between two rows) run *without* an explicit transaction can leave the database in a broken half-applied state if the second statement fails — always wrap related writes in BEGIN/COMMIT.
- `ROLLBACK TO savepoint` doesn't release/finish the transaction itself — you still need a matching `RELEASE`, or the outer `COMMIT`/`ROLLBACK`, to finish things off.
- A CHECK constraint violation mid-transaction (e.g. balance going negative) is exactly the kind of failure a transaction protects against — catch it and ROLLBACK instead of leaving a partial debit applied.

## When it matters
Any time more than one write needs to succeed or fail together — transfers, multi-table updates, anything where a partial failure would corrupt data.

## One-line recap example
```sql
BEGIN;
UPDATE accounts SET balance = balance - 200 WHERE owner = 'Alice';
UPDATE accounts SET balance = balance + 200 WHERE owner = 'Bob';
COMMIT;
```
