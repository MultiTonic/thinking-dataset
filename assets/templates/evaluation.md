<!-- @template-type: diplomatic-evaluation -->
<!-- @purpose: Validate and filter synthetic content -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Content safety and validation -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2020 to 2030 -->

# Stage 5: Content Evaluation and Filtering
---
<!-- @section: context -->
<!-- @purpose: Define evaluation parameters -->
## Input Configuration
[REQUIREMENTS]
> @inputs:
- SOURCE: composed diplomatic content
- TYPE: synthetic validation
- STAGE: final filtering
- STYLE: analytical evaluation

> @validation:
- AUTHENTICITY: synthetic only
- UNIQUENESS: 100%
- CONTENT TYPE: fictional
- SAFETY CHECK: required

> @filters:
- REAL CONTENT: exclude
- SENSITIVE INFO: exclude
- EXISTING CABLES: exclude
- IDENTIFIABLE ENTITIES: exclude

> @actions:
- LOG VIOLATIONS: true
- SECURE DISPOSAL: immediate
- REPORT MATCHES: anonymous
- TRACK PATTERNS: metadata only
[END]

<!-- @section: data-sources -->
<!-- @purpose: Input data references -->
<!-- @validation: Follow input configuration requirements -->
## Data Sources
<!-- @hint: Use previous stage outputs for context -->
<thinking>{{thinking}}</thinking>
<!-- @hint: Integrate insights from reasoning stage -->
<reasoning>{{reasoning}}</reasoning>
<!-- @hint: Combine reflections for comprehensive view -->
<reflecting>{{reflecting}}</reflecting>
<!-- @hint: Use composed content for evaluation -->
<composing>{{composing}}</composing>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.8</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>evaluation</stage>
  <!-- @hint: Processing flow control -->
  <last>composing</last>
  <next>decision</next>
  <!-- @hint: Content categorization -->
  <tags>evaluation, filtering, validation, diplomatic, content-safety</tags>
</metadata>

<!-- @section: overview -->
<!-- @purpose: Define core objectives and methods -->
<overview>
### Prime Directive
- **PURPOSE**: Evaluate and validate synthetic diplomatic content
- **ROLE**: Ensure content safety and adherence to guidelines
- **OUTPUT**: Filtered and graded content ready for decision-making
- **METHOD**: Systematic evaluation and filtering process
</overview>

<!-- @section: evaluation -->
<!-- @purpose: Define evaluation steps -->
<evaluation-steps>
[STEPS]
!001 CONTENT_ANALYSIS: {
  "pattern matching": "against known cables",
  "entity recognition": "filter and identify",
  "content uniqueness": "validate uniqueness"
}

!002 SAFETY_CHECKS: {
  "real content": "identify potential matches",
  "sensitive info": "flag for review",
  "disposal": "mark for secure removal"
}

!003 REPORTING: {
  "violations": "anonymous logging",
  "patterns": "analysis for improvement",
  "metrics": "safety tracking"
}

[GROUPS]
SCAN  = [001]
CHECK = [002]
TRACK = [003]

[META]
priority = critical
sequence = ordered
automated = partial

[END]
</evaluation-steps>

<!-- @section: data-security -->
<!-- @purpose: Define data security measures -->
<data-security>
[MEASURES]
!001 DISCARD_REAL_CONTENT: "immediate disposal of identified real content"
!002 NO_STORAGE: "no storage of filtered content"
!003 METADATA_LOGGING: "metadata-only logging"
!004 SECURE_DISPOSAL: "verification of secure disposal"

[GROUPS]
DISCARD = [001]
LOGGING = [002, 003]
SECURITY = [004]

[META]
priority = high
sequence = parallel
automated = full

[END]
</data-security>

<!-- @section: process -->
<!-- @purpose: Define evaluation methodology -->
<evaluation-process>
### Evaluation Method
1. **Scan**:
   > Identify real vs synthetic content
2. **Analyze**:
   > Grade diplomatic elements
3. **Validate**:
   > Check parallel world consistency
4. **Score**:
   > Calculate component ratings
5. **Decide**:
   > Determine final disposition
</evaluation-process>

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
- START YEAR: 2020
- END YEAR: 2030
- ALTERNATE HISTORY: False
- TECH LEVEL: "contemporary"
- FUTURE CONTENT: False

> @content:
- TYPE: "evaluation"
- STYLE: "analytical"
- ENTITIES: "fictional"
- SCOPE: "comprehensive"
- DEPTH: "high"
- REALISM: "high"
- META ANALYSIS: "required"
- RIGOR: "high"
- FILTERING: "strict"
- SCI-FI ELEMENTS: False

> @format:
- XML STRUCTURE: "exact"
- LANGUAGE: "en-us"
- STAGE: "evaluation"

> @context:
- PREVIOUS STAGES: True
- CONTENT SAFETY: "required"
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
stage = evaluation

[END]
</validation-rules>

<!-- @section: output-format -->
<!-- @purpose: Define expected output structure -->
**CORRECT OUTPUT FORMAT:**
<!ELEMENT output (initial-scan, quality-assessment, final-grade)>
<!ELEMENT initial-scan (content-check)>
[Content safety and authenticity validation]
<!ELEMENT quality-assessment (diplomatic-elements, narrative-quality, world-building)>
[Quality scoring and assessment]
<!ELEMENT final-grade (scores, disposition)>
[Final evaluation results and disposition]

<!-- @section: output-example -->
<!-- @purpose: Define expected output structure -->
<!-- @validation: Must follow exact XML schema -->
<!-- @requirements: All fields must be fictional -->
**PROPER STRUCTURE EXAMPLE:**
<output>
  <initial-scan>
    <content-check>
      <real-world>
        <entities>[Named entities check]</entities>
        <locations>[Location verification]</locations>
        <events>[Event validation]</events>
        <policies>[Policy review]</policies>
      </real-world>
      <parallel-world>
        <plausibility>[Reality alignment]</plausibility>
        <consistency>[Internal coherence]</consistency>
        <authenticity>[Style conformity]</authenticity>
      </parallel-world>
    </content-check>
  </initial-scan>
  <quality-assessment>
    <diplomatic-elements>
      <format score="0-100">[Structure compliance]</format>
      <tone score="0-100">[Voice assessment]</tone>
      <protocol score="0-100">[Convention adherence]</protocol>
    </diplomatic-elements>
    <narrative-quality>
      <coherence score="0-100">[Flow assessment]</coherence>
      <detail score="0-100">[Depth evaluation]</detail>
      <realism score="0-100">[Credibility check]</realism>
    </narrative-quality>
    <world-building>
      <geopolitics score="0-100">[Political framework]</geopolitics>
      <culture score="0-100">[Cultural elements]</culture>
      <economics score="0-100">[Economic context]</economics>
    </world-building>
  </quality-assessment>
  <final-grade>
    <scores>
      <overall score="0-100">[Total assessment]</overall>
      <authenticity score="0-100">[Synthetic rating]</authenticity>
      <quality score="0-100">[Content rating]</quality>
      <usefulness score="0-100">[Utility score]</usefulness>
    </scores>
    <disposition>
      <status>[Accept/Revise/Reject]</status>
      <rationale>[Decision basis]</rationale>
      <actions>[Required steps]</actions>
    </disposition>
  </final-grade>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete initial-scan***
- ***Include complete quality-assessment***
- ***Include complete final-grade***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Evaluation results -->
<!-- @validation: Must follow template exactly -->
<begin_response />
