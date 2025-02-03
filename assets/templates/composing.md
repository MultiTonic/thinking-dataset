<!-- @template-type: diplomatic-composition -->
<!-- @purpose: Transform all prior inputs into formal diplomatic cable -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Professional diplomatic cable creation -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2025 to 2035 -->
---
# Stage 4: Diplomatic Cable Composition

<!-- @section: context -->
<!-- @purpose: Define input parameters and constraints -->
## Input Configuration
[REQUIREMENTS]
> @inputs:
- SOURCE: diplomatic cables
- SAMPLE SIZE: 20k-100k chars
- TYPE: random selection
- STYLE: professional diplomatic

> @content:
- UNIQUENESS: 100%
- EXTRACTION: structural patterns only
- COMBINATION: all stage outputs
- INSPIRATION: real world snippets

> @prohibited:
- CONTENT COPYING: false
- SAMPLE COMBINING: false
- REAL DETAILS: false
- INSPIRATION COMBINING: false
- SCI-FI ELEMENTS: false
- FUTURISTIC CONTENT: false
[END]

<!-- @section: data-sources -->
<!-- @purpose: Input data references -->
<!-- @validation: Follow input configuration requirements -->
## Data Sources
<!-- @hint: Use provided seeds for inspiration -->
<inspirations>{{seeds}}</inspirations>
<!-- @hint: Use previous stage outputs for context -->
<thinking>{{thinking}}</thinking>
<!-- @hint: Integrate insights from reasoning stage -->
<reasoning>{{reasoning}}</reasoning>
<!-- @hint: Combine reflections for comprehensive view -->
<reflecting>{{reflecting}}</reflecting>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>0.0.3</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>composing</stage>
  <!-- @hint: Processing flow control -->
  <last>reflecting</last>
  <next>evaluation</next>
  <!-- @hint: Content categorization -->
  <tags>diplomatic-cable, composition, final-output, synthetic-content, diplomatic, communication</tags>
</metadata>

<!-- @section: overview -->
<!-- @purpose: Define core objectives and methods -->
<overview>
### Prime Directive
- **PURPOSE**: Transform inputs into diplomatic cable
- **ROLE**: Convert narrative into formal communication
- **OUTPUT**: XML-structured cable document
- **METHOD**: Systematic diplomatic translation
</overview>

<!-- @section: process -->
<!-- @purpose: Define cable composing methodology -->
<!-- @visibility: Internal only, not for output -->
<composing-process>
### Composing Method
1. **Analyze**:
   > Review cable requirements and format specifications
2. **Structure**:
   > Map required sections and components
3. **Compose**:
   > Create a professional diplomatic cable
4. **Verify**:
   > Ensure compliance and completeness
</composing-process>

<!-- @section: instructions -->
<!-- @purpose: Critical rules and constraints -->
<!-- @priority: Highest -->
<!-- @enforcement: Strict -->
<critical-instruction>
### CRITICAL RULES
***IMPORTANT***
[CONSTRAINTS]
> @spatial:
- EARTH ONLY: True
- REAL LOCATIONS: True
- FICTIONAL PLACES: False
- SPACE CONTEXT: "terrestrial"

> @temporal:
- START YEAR: 2025
- END YEAR: 2035
- ALTERNATE HISTORY: False
- TECH LEVEL: "contemporary"
- FUTURE CONTENT: False

> @content:
- TYPE: "fictional"
- STYLE: "diplomatic"
- ENTITIES: "fictional"
- SCOPE: "comprehensive"
- DEPTH: "high"
- REALISM: "high"
- META ANALYSIS: "required"
- RIGOR: "high"
- INSIGHTS: "diplomatic"
- SCI-FI ELEMENTS: False

> @format:
- XML STRUCTURE: "exact"
- LANGUAGE: "en-us"
- STAGE: "composing"

> @context:
- PREVIOUS STAGES: True
- STRUCTURAL INSPIRATION: True
- PROFESSIONAL TONE: True
- STAGES COHERENCE: "high"

> @prohibited:
- PROCESS INCLUSION: False
- FORMAT MARKERS: False
- OUTPUT WRAPPING: False
- CONTENT BLOCKS: False
- REAL REFERENCES: False
- NON-EARTH: False
- FUTURE-TECH: False
- REAL ENTITIES: False
- PROCESS LEAKAGE: False
- SCI-FI ELEMENTS: False
- FUTURISTIC CONTENT: False
[END]

<!-- @section: validation -->
<!-- @purpose: Define validation rules -->
<validation-rules>
[RULES]
!001 XML_SCHEMA: "follow exact XML schema"
!002 FICTIONAL: "all content must be fictional" 
+003 TONE: "professional diplomatic tone"
+004 CONSTRAINTS: "follow all constraint blocks"
!005 NO_SCIFI: "no sci-fi/futuristic elements"
!006 NO_REAL_WORLD: "no real-world content"
+007 PARALLEL_WORLD: "use parallel world content"

[GROUPS]
ALL  = [001, 002]
MUST = [003-007]
CRIT = [001, 002, 005, 006]
HIGH = [003, 004, 007]

[META]
enforced = True
validated = False
stage = composing

[END]
</validation-rules>

<!-- @section: output-format -->
<!-- @purpose: Define expected output structure -->
**CORRECT OUTPUT FORMAT:**
<!ELEMENT output (initial-draft, cable-components, final-cable)>
<!ELEMENT initial-draft (header)>
[Standard cable header structure]
<!ELEMENT cable-components (summary, main-content)>
[Numbered main paragraphs]
<!ELEMENT final-cable (signature, administrative)>
[Official cable completion]

<!-- @section: output-example -->
<!-- @purpose: Define expected output structure -->
<!-- @validation: Must follow exact XML schema -->
<!-- @requirements: All fields must be fictional -->
**PROPER STRUCTURE EXAMPLE:**
<output>
  <initial-draft>
    <header>
      <precedence>IMMEDIATE</precedence>
      <classification>
        <primary>[Classification Level]</primary>
        <addendum>[Special Handling]</addendum>
        <channels>[Distribution List]</channels>
      </classification>
      <origin>
        <mission>[Embassy Name]</mission>
        <office>[Office Code]</office>
        <location>[City, Country]</location>
      </origin>
      <routing>
        <to>[Primary Recipients]</to>
        <info>[Info Recipients]</info>
        <attention>[Specific Office]</attention>
      </routing>
      <identifiers>
        <reference>[Cable Numbers]</reference>
        <tags>[Policy Tags]</tags>
        <subject>[Clear Title]</subject>
      </identifiers>
    </header>
  </initial-draft>
  <cable-components>
    <summary>
      <classification>[Section Level]</classification>
      <overview>1. [Executive Summary]</overview>
      <key-points>
        <point>[Main Point A]</point>
        <point>[Main Point B]</point>
        <point>[Main Point C]</point>
      </key-points>
    </summary>
    <main-content>
      <background>
        <classification>[Section Level]</classification>
        <context>2. [Background Info]</context>
        <details>[Supporting Info]</details>
      </background>
      <analysis>
        <classification>[Section Level]</classification>
        <discussion>3. [Core Analysis]</discussion>
        <points>
          <major>[Key Points]</major>
          <supporting>[Evidence]</supporting>
          <implications>[Impacts]</implications>
        </points>
      </analysis>
      <comment>
        <classification>[Section Level]</classification>
        <assessment>4. [Post Analysis]</assessment>
        <strategic>[Strategic View]</strategic>
        <recommendations>[Actions]</recommendations>
      </comment>
    </main-content>
  </cable-components>
  <final-cable>
    <signature>
      <post>[Embassy Name]</post>
      <drafted>
        <by>[Drafting Officers]</by>
        <office>[Office Code]</office>
        <date>[Date]</date>
      </drafted>
      <cleared>
        <by>[Clearing Officers]</by>
        <office>[Office Code]</office>
      </cleared>
      <approved>
        <by>[Authority]</by>
        <title>[Title]</title>
      </approved>
    </signature>
    <administrative>
      <classification>
        <authority>[Class Authority]</authority>
        <reason>[Reason Code]</reason>
        <declassification>[Declass Info]</declassification>
      </classification>
      <dissemination>
        <restrictions>[Handling Notes]</restrictions>
        <distribution>[Distro Limits]</distribution>
      </dissemination>
    </administrative>
  </final-cable>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete initial-draft***
- ***Include complete cable-components***
- ***Include complete final-cable***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Diplomatic cable -->
<!-- @validation: Must follow exact cable format -->
<!-- @schema: Standard diplomatic cable structure -->
<begin_response />
