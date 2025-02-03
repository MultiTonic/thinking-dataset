<!-- @template-type: diplomatic-decision -->
<!-- @purpose: Process evaluation results and determine actions -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Strategic decision making and action planning -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2025 to 2035 -->

# Stage 6: Strategic Decision Making
---
<!-- @section: context -->
<!-- @purpose: Define decision parameters -->
## Input Configuration
[REQUIREMENTS]
> @inputs:
- SOURCE: evaluation results
- TYPE: decision analysis
- STAGE: final action
- STYLE: strategic planning

> @processing:
- EVALUATE: composite scores
- ANALYZE: flagged content
- REVIEW: improvement suggestions
- ASSESS: training value

> @decisions:
- ARCHIVE: valuable samples
- REFINE: promising content
- DISCARD: rejected content
- TRAIN: successful patterns

> @actions:
- PATTERN EXTRACTION: true
- MODEL UPDATING: conditional
- FEEDBACK LOOP: required
- METRICS TRACKING: enabled
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
<!-- @hint: Use evaluation results for decision making -->
<evaluation>{{evaluation}}</evaluation>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>0.0.3</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>decision</stage>
  <!-- @hint: Processing flow control -->
  <last>evaluation</last>
  <next>action</next>
  <!-- @hint: Content categorization -->
  <tags>decision, analysis, strategic-planning, diplomatic, action-planning</tags>
</metadata>

<!-- @section: process -->
<!-- @purpose: Define decision-making methodology -->
<decision-process>
### Decision Method
1. **Review**:
   > Analyze evaluation results and flagged content
2. **Assess**:
   > Determine content value and potential actions
3. **Decide**:
   > Make archiving, training, or refinement decisions
4. **Plan**:
   > Develop action plans for immediate and long-term steps
5. **Document**:
   > Record decisions, rationale, and metrics
</decision-process>

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
- TYPE: "decision"
- STYLE: "strategic"
- ENTITIES: "fictional"
- SCOPE: "comprehensive"
- DEPTH: "high"
- REALISM: "high"
- META ANALYSIS: "required"
- RIGOR: "high"
- ACTIONABLE: "required"
- SCI-FI ELEMENTS: False

> @format:
- XML STRUCTURE: "exact"
- LANGUAGE: "en-us"
- STAGE: "decision"

> @context:
- PREVIOUS STAGES: True
- STRATEGIC ALIGNMENT: "required"
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
stage = decision

[END]
</validation-rules>

<!-- @section: output-format -->
<!-- @purpose: Define expected output structure -->
**CORRECT OUTPUT FORMAT:**
<!ELEMENT output (analysis-review, decision-matrix, action-plan)>
<!ELEMENT analysis-review (evaluation-summary, content-value)>
[Review of evaluation results and content value assessment]
<!ELEMENT decision-matrix (archive-decision, training-decision, refinement-decision)>
[Strategic decisions on content handling]
<!ELEMENT action-plan (immediate-actions, long-term-actions, documentation)>
[Concrete action steps and documentation]

<!-- @section: output-example -->
<!-- @purpose: Define expected output structure -->
<!-- @validation: Must follow exact XML schema -->
<!-- @requirements: All fields must be fictional -->
**PROPER STRUCTURE EXAMPLE:**
<output>
  <analysis-review>
    <evaluation-summary>
      <scores>[Complete evaluation results]</scores>
      <flags>[Critical issues identified]</flags>
      <patterns>[Notable trends found]</patterns>
    </evaluation-summary>
    <content-value>
      <training>[ML/Pattern value]</training>
      <reference>[Archive importance]</reference>
      <improvement>[Enhancement potential]</improvement>
    </content-value>
  </analysis-review>
  <decision-matrix>
    <archive-decision>
      <status>[Archive/Discard decision]</status>
      <rationale>[Decision reasoning]</rationale>
      <classification>[Security level]</classification>
    </archive-decision>
    <training-decision>
      <status>[Train/Exclude choice]</status>
      <value>[Pattern significance]</value>
      <application>[Use context]</application>
    </training-decision>
    <refinement-decision>
      <status>[Refine/Reject status]</status>
      <approach>[Improvement method]</approach>
      <priority>[Action urgency]</priority>
    </refinement-decision>
  </decision-matrix>
  <action-plan>
    <immediate-actions>
      <archive>[Storage actions]</archive>
      <training>[Model updates]</training>
      <feedback>[System adjustments]</feedback>
    </immediate-actions>
    <long-term-actions>
      <patterns>[Pattern updates]</patterns>
      <metrics>[Performance tracking]</metrics>
      <improvements>[System upgrades]</improvements>
    </long-term-actions>
    <documentation>
      <decisions>[Choice records]</decisions>
      <metrics>[Success criteria]</metrics>
      <timeline>[Action schedule]</timeline>
    </documentation>
  </action-plan>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete analysis-review***
- ***Include complete decision-matrix***
- ***Include complete action-plan***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Decision results -->
<!-- @validation: Must follow template exactly -->
<begin_response />
