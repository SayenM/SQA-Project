# SQA-Project

# Banking System Project

**CSCI 3060U – Winter 2025**  
Course Project – Agile Software Development

## Overview
This repository contains our group implementation of a **Banking System**, developed for the CSCI 3060U course project. The system consists of two console-based applications:

- **Front End**: Simulates an Automated Teller Machine (ATM) for daily banking transactions.
- **Back End**: Processes transaction files in batch mode to update bank account records.

The project follows **Agile Development principles**, emphasizing incremental development, testing, and continuous integration.

---

## System Components

### Front End
The Front End reads a current bank accounts file, processes a sequence of banking transactions, and outputs a daily bank account transaction file.

Supported transactions:
- `login`
- `logout`
- `withdrawal`
- `transfer`
- `paybill`
- `deposit`
- `create` (admin only)
- `delete` (admin only)
- `disable` (admin only)
- `changeplan` (admin only)

Features:
- Console-based application
- Text file input/output only
- Graceful handling of invalid input
- Enforces transaction and session constraints

---

### Back End
The Back End applies transactions from merged transaction files to update account data.

Responsibilities include:
- Reading the Master Bank Accounts File
- Applying all valid transactions
- Generating:
  - A new Master Bank Accounts File
  - A new Current Bank Accounts File
- Calculating transaction fees based on account plans
- Logging constraint violations and fatal errors

---

## File Formats
All files use **fixed-length text records**, following the specifications provided in the project description. These include:

- Current Bank Accounts File
- Bank Account Transaction File
- Master Bank Accounts File
- Merged Transaction File

---

## Development Practices
- Agile, iterative development
- Pair programming
- Continuous testing
- Frequent integration and releases
- Focus on simplicity and correctness

---

## How to Run
Both the Front End and Back End are executed from the command line and rely on text files for input and output.

> Detailed run instructions will be added as the project progresses.

---

## Team
Completed by a team of **3–4 students** for the CSCI 3060U Winter 2025 course.
