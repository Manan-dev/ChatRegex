# ChatRegex for Detective Novels

**COSC 524 - Natural Language Processing - Project 1**

Objective: Develop a REGEX-based chatbot for the statistical text analysis of crime novels.

Source: [Project Gutenberg](https://www.gutenberg.org/)

## Dependencies

- Python 3.10.X

## Usage

```
usage: main.py [-h] -i INPUT [-d]

ChatRegex

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to input text file
  -d, --debug           enable debug mode
```

Example:

```bash
python3 main.py -i ./dataset/the_man_the_brown_suit.txt
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

#### [+ PROMPT VARIATIONS](PROMPTS.md)

### Part 3 - Results Generation

- Generate responses for the prompted questions.
- Should produce precise results and in natural, well-structured English, as if interacting with a human investigator.
