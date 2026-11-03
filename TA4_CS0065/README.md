# Technical Assessment 4: Knowledge Representation and Reasoning

**CS0065 - Intelligent Systems, FEU Institute of Technology**  
**Student:** Dela Cruz, Robie D. | **Section:** AN43 | **Professor:** Ms. Tan

A Python weather activity advisor demonstrating a knowledge base, rule-based
reasoning (RBR), and case-based reasoning (CBR). Both systems use the same input
facts so their decisions can be compared directly. All computation runs locally.

## Run

Use **Python 3.10 or later**. No external packages, API keys, or internet
connection are needed to run the program.

```bash
python ta4_reasoning.py
```

On Windows, `py ta4_reasoning.py` also works if Python Launcher is installed.
Run commands from this repository's root directory.

```bash
# Run the two reasoning methods separately.
python ta4_reasoning.py --mode rbr
python ta4_reasoning.py --mode cbr

# Read the six facts from an editable JSON file.
python ta4_reasoning.py --facts examples/weather.json

# Revise the retrieved solution manually; Enter keeps the proposal.
python ta4_reasoning.py --mode cbr --interactive

# Demonstrate revision without an interactive prompt.
python ta4_reasoning.py --mode cbr --revision "Move the activity to an indoor venue."

# Export the case base after retaining the new case.
python ta4_reasoning.py --mode cbr --save-cases retained_cases.json

# Show all command options.
python ta4_reasoning.py --help
```

Each run starts with three seed cases. Retention adds a fourth case in memory.
`--save-cases` exports that final list; it does not make later runs automatically
reload the exported cases. No revision flag means the retrieved solution is
kept unchanged. EOF during an interactive prompt also keeps it unchanged.

## Repository contents

```text
ta4-knowledge-reasoning/
  ta4_reasoning.py                  Complete runnable laboratory solution
  README.md                        Setup, explanation, reflection, submission
  requirements.txt                 Confirms no external runtime dependencies
  .gitignore                       Excludes caches and local generated files
  .gitattributes                   Consistent line endings and binary files
  .github/workflows/python-checks.yml
  examples/weather.json            Sample input
  examples/combined_output.txt      Actual output of the default run
  examples/rbr_output.txt           Actual RBR execution output
  examples/cbr_output.txt           Actual CBR execution output
  examples/cbr_revised_output.txt   Actual execution with manual revision
  docs/TA4_DelaCruz.docx            Completed assessment, original design
  docs/TA4_DelaCruz.pdf             Code, answers, and output images in one PDF
  docs/screenshots/                 Captures of the program's actual output
  tests/test_reasoning.py           Standard-library unittest checks
```

## Part 1: Knowledge representation

The use case is deciding how to prepare for an outdoor activity given the
weather and activity context. The `FACTS` dictionary contains six facts,
and `CATEGORIES` groups them into three explicit categories.

| Category | Fact | Sample value | Unit/type |
| --- | --- | --- | --- |
| Temperature | `temperature` | 32 | degrees Celsius |
| Weather | `humidity` | 85 | percent |
| Weather | `is_raining` | true | Boolean |
| Weather | `wind_speed` | 12 | km/h |
| Activity context | `is_daytime` | true | Boolean |
| Activity context | `outdoor_activity` | true | Boolean |

`validate_facts` requires these exact six keys, numeric values in the documented
input ranges, and real Boolean values for the three Boolean facts. The accepted
numeric ranges are -20 to 50 degrees Celsius, 0 to 100 percent humidity, and
0 to 200 km/h wind. These are teaching input limits, not weather forecasts.
Missing keys, unexpected keys, invalid types, and invalid numbers produce a
readable command-line error.

## Part 2: Rule-based reasoning

Five Python functions implement IF-THEN rules:

| Rule | IF | THEN |
| --- | --- | --- |
| `rule_hot` | temperature > 30 | Turn on a fan or air conditioner. |
| `rule_rain` | raining | Bring an umbrella. |
| `rule_humid_heat` | temperature > 30 AND humidity >= 80 | Drink water and take breaks. |
| `rule_wind` | wind speed >= 30 | Secure loose outdoor items. |
| `rule_outdoor_rain` | outdoor activity AND raining | Move the activity indoors. |

The rule functions and their conditions form the rule knowledge base. `infer`
copies the facts into working memory, loops through every rule, records which
ones fired, and returns every inferred action. This is a single-pass inference
engine: actions do not become new facts. It reports when no rule matches.

With the sample facts, the hot, rain, humid heat, and outdoor rain rules fire.
The wind rule does not fire because 12 km/h is below 30 km/h.

## Part 3: Case-based reasoning

Three seed cases store a complete problem dictionary and its matching solution:

| Case | Temp. | Humidity | Rain | Wind | Daytime | Outdoors |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 31 | 80 | true | 10 | true | true |
| 2 | 27 | 55 | false | 12 | true | true |
| 3 | 20 | 70 | true | 40 | false | false |

Case 1 recommends an umbrella, water, and moving indoors. Case 2 recommends
proceeding outdoors with water. Case 3 recommends staying indoors and securing
loose outdoor items. Their solutions are illustrative past cases.

1. **Retrieve:** Compare the new problem with every case. Boolean features score
   1 for a match and 0 otherwise. Numeric features score
   `max(0, 1 - abs(new - past) / range)`, with ranges of 50 degrees Celsius,
   100 humidity percentage points, and 100 km/h. Average all six scores;
   every feature has equal weight. A tie selects the earlier case.
2. **Reuse:** Return the solution of the highest-scoring case.
3. **Revise:** Accept a manual replacement with `--interactive` or `--revision`,
   or keep the original proposal unchanged.
4. **Retain:** Append the new problem and final solution to the case base.
   The problem is copied so later edits cannot overwrite the retained case.

For example, Case 1 receives numeric scores 0.98, 0.95, and 0.98, plus three
Boolean matches: `(0.98 + 0.95 + 0.98 + 1 + 1 + 1) / 6 = 0.985`.
The sample similarities are **98.50%, 76.67%, and 55.50%**. Case 1 wins.
After retention, the case count changes from **3 to 4**. Similarity measures
feature resemblance; it is not a probability that the recommendation is correct.

## Part 4: Comparative reflection

In this implementation, RBR is easier to implement because each condition maps
directly to an action, while CBR also needs a case base, a similarity measure,
and revision and retention steps. CBR is more flexible for unstructured or
unfamiliar problems when relevant past cases exist, because a partial match can
provide a starting solution that a person can adapt. Its flexibility still
depends on how the problem features are represented. For continuously changing
experience, CBR can be more suitable because verified new cases can be retained
without rewriting every rule. However, obsolete cases and unsuitable similarity
weights must be reviewed; RBR remains useful when stable, explicit policies
must be enforced while input values change. Real-world RBR applications include
eligibility checks and equipment alarms, while CBR applications include
technical support and adapting previous repair plans to similar faults.

The sample demonstrates this difference: RBR returns four independent actions
with a trace of the rules that fired, while CBR returns one recommendation from
the most similar past situation and adds a new case. CBR is not guaranteed to
be more accurate simply because it retains more cases. The demonstration uses
manual review rather than automatically verifying whether the final advice
worked.

## Test

```bash
python -m unittest discover -s tests -v
```

The 15 tests check category coverage, all matching rules, threshold boundaries,
no matches, numeric and Boolean similarity, nearest-case selection, ties, an
empty case base, manual revision, retention without shared references, input
validation, and command-line revision/export and errors. The GitHub Actions
workflow runs the tests and sample execution on Python 3.10 and 3.12. Local
tests have passed; the workflow runs after the repository is pushed to GitHub.

## Assessment submission

Submit `ta4_reasoning.py` and `docs/TA4_DelaCruz.pdf`. The PDF includes the
knowledge base and use case, RBR and CBR explanations, reflection, the complete
laboratory source code, and images of actual execution output. The editable
DOCX is also included. The original FEU layout, logo, tables, and instructions
are preserved; the completed answers follow the existing laboratory section.

The supplied brief labels this as TA4 but mentions TA3 and TA2 in some general
instructions, and omits the Task 3B heading. This submission follows TA4 and
implements Retrieve as part of the required 4R cycle. Only the supplied student
name is filled in; no partner name has been invented.

## Put this project on GitHub

Create an empty GitHub repository named `ta4-knowledge-reasoning`, then run
these commands inside the extracted project folder. Replace `YOUR_USERNAME`
with your account name. Git must be installed for this method.

```bash
git init
git add .
git commit -m "Complete TA4 knowledge representation and reasoning assessment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ta4-knowledge-reasoning.git
git push -u origin main
```

The archive contains the project source and documents, not an initialized Git
history. Keep the hidden `.github`, `.gitignore`, and `.gitattributes` files
when extracting. This package is ready to upload; it has not been published
to GitHub.
