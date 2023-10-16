# ChatRegex for Detective Novels

**COSC 524 - Natural Language Processing - Project 1**

Authors: Andrei Cozma, Manan Patel, Tulsi Tailor, Zac Perry

Objective: Develop a REGEX-based chatbot for the statistical text analysis of crime novels.

Source of Novels: [Project Gutenberg](https://www.gutenberg.org/)

## Dependencies

- Python 3.10.X

## Usage

```
usage: main.py [-h] -i INPUT [-v] [-t]

ChatRegex

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to input text file
  -v, --verbose         increase console output verbosity
  -t, --test            disables the interactive chat mode and runs a series of example prompt test cases
```

Example Usage:

```bash
python3 main.py -i ./dataset/the_sign_of_the_four.txt
```

Corresponding Output:

```
================================================================================

 ██████╗██╗  ██╗ █████╗ ████████╗   ██████╗ ███████╗ ██████╗ ███████╗██╗  ██╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝   ██╔══██╗██╔════╝██╔════╝ ██╔════╝╚██╗██╔╝
██║     ███████║███████║   ██║█████╗██████╔╝█████╗  ██║  ███╗█████╗   ╚███╔╝ 
██║     ██╔══██║██╔══██║   ██║╚════╝██╔══██╗██╔══╝  ██║   ██║██╔══╝   ██╔██╗ 
╚██████╗██║  ██║██║  ██║   ██║      ██║  ██║███████╗╚██████╔╝███████╗██╔╝ ██╗
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝

INFO: Reading data from file: ./dataset/the_sign_of_the_four.txt
INFO: Preprocessing data...
INFO: Extracting body of text...
INFO: Normalizing chapter headings...
INFO: Normalizing character set...
INFO: Starting interactive chat session...
================================================================================
AI : Hello! What can I do for you?
--------------------------------------------------------------------------------
You: hi
AI : Hello! How can I help you?
--------------------------------------------------------------------------------
You: 
```

## Special Commands

```
================================================================================
AI : Hello! What can I do for you?
--------------------------------------------------------------------------------
You: help
AI : Special commands you can use: 
  help, h       - Print this help message 
  example, ex   - Print some example prompts (e.g. `example` or `example 5` to print 5 examples) 
  exit, quit, q - Exit the program.
--------------------------------------------------------------------------------
You: ex
AI : Example queries:
 - "Words around perpetrator"
--------------------------------------------------------------------------------
You: ex 3
AI : Example questions you can ask:
 - "Identify the chapter and sentence where the detective first appears."
- "When is the killer first mentioned"
- "Tell me when the criminal is first mentioned in the book."
--------------------------------------------------------------------------------
You: quit
AI : Farewell!
```

## Deliverables

- Source Code
- Report (max 2 pages, excluding references)
- Presentation and live analysis
  - Choice between pre-recorded and a live, in-class delivery

### Crime novels

- [The Sign of the Four by Arthur Conan Doyle](https://www.gutenberg.org/ebooks/2097)
- [The Murder on the Links by Agatha Christie](https://www.gutenberg.org/ebooks/58866)
- [The Man in the Brown Suit by Agatha Christie](https://www.gutenberg.org/ebooks/61168)

### Part 1 - Prompts

- Use regex from Python and the packages available in Python 3.10.
- Prompt parsing should allow flexibility in how the request/question is formulated.

### Part 2 - Novel Analysis

- Aims to analyze the frequency of occurrence of the protagonists and the perpetrator(s) across the novel - per chapter and per sentence in a chapter, the mention of the crime and other circumstances surrounding the antagonists.
- The ultimate objective is to use basic NLP tools to observe any patterns in plot structures across the works of one or all authors.

To analyze and report on:

1. When does the investigator (or a pair) occur for the first time.
2. When is the crime first mentioned, the type of the crime, and the details.
3. When is the perpetrator first mentioned.
4. What are the three words that occur around the perpetrator on each mention
   - (i.e., the three words preceding and the three words following the mention of a perpetrator)
5. When and how the detective/detectives and the perpetrators co-occur
6. When are other suspects first introduced

The above should include the **chapter # and the sentence(s) # in a chapter**.

### Part 3 - Results Generation

- Generate responses for the prompted questions.
- Should produce precise results and in natural, well-structured English, as if interacting with a human investigator.
