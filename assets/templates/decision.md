<!-- @template-type: diplomatic-decision -->
<!-- @purpose: Process evaluation results and determine actions -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -->
<!-- @context: Strategic decision making and action planning -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2020 to 2030 -->

# Stage 6: Strategic Decision Making
---
<!-- @section: context -->
<!-- @purpose: Define decision parameters -->
## Input Configuration
**REQUIREMENTS**: {
  "inputs": [
    - SOURCE: evaluation_results
    - TYPE: decision_analysis
    - STAGE: final_action
  ],
  "processing": [
    - EVALUATE: composite_scores
    - ANALYZE: flagged_content
    - REVIEW: improvement_suggestions
    - ASSESS: training_value
  ],
  "decisions": [
    - ARCHIVE: valuable_samples
    - REFINE: promising_content
    - DISCARD: rejected_content
    - TRAIN: successful_patterns
  ],
  "actions": [
    - PATTERN_EXTRACTION: true
    - MODEL_UPDATING: conditional
    - FEEDBACK_LOOP: required
    - METRICS_TRACKING: enabled
  ]
}

## Data Sources
<thinking>{{thinking}}</thinking>
<reasoning>{{reasoning}}</reasoning>
<reflecting>{{reflecting}}</reflecting>
<composing>{{composing}}</composing>
<evaluation>{{evaluation}}</evaluation>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.7</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>decision</stage>
  <!-- @hint: Processing flow control -->
  <last>evaluation</last>
  <next>action</next>
  <!-- @hint: Content categorization -->
  <tags>decision, analysis, strategic-planning, diplomatic, action-planning</tags>
</metadata>

<!-- @section: output-format -->
<!-- @purpose: Define decision output structure -->
<output-format>
### Decision Structure
[DETERMINE ACTIONS FOR EVALUATED CONTENT]

<analysis-review>
  <evaluation-summary>
    <scores>[Composite evaluation results]</scores>
    <flags>[Critical issues summary]</flags>
    <patterns>[Identified trends]</patterns>
  </evaluation-summary>
  <content-value>
    <training>[ML training potential]</training>
    <reference>[Archive value]</reference>
    <improvement>[Enhancement potential]</improvement>
  </content-value>
</analysis-review>

<decision-matrix>
  <archive-decision>
    <status>[ARCHIVE/DISCARD]</status>
    <rationale>[Storage justification]</rationale>
    <classification>[Access level]</classification>
  </archive-decision>
  
  <training-decision>
    <status>[TRAIN/EXCLUDE]</status>
    <value>[Pattern importance]</value>
    <application>[Usage context]</application>
  </training-decision>
  
  <refinement-decision>
    <status>[REFINE/REJECT]</status>
    <approach>[Improvement method]</approach>
    <priority>[Urgency level]</priority>
  </refinement-decision>
</decision-matrix>

<action-plan>
  <immediate-actions>
    <archive>[Storage instructions]</archive>
    <training>[Model update steps]</training>
    <feedback>[Pipeline adjustments]</feedback>
  </immediate-actions>
  
  <long-term-actions>
    <patterns>[Pattern database updates]</patterns>
    <metrics>[Performance tracking]</metrics>
    <improvements>[System enhancements]</improvements>
  </long-term-actions>
  
  <documentation>
    <decisions>[Choice rationale]</decisions>
    <metrics>[Success measures]</metrics>
    <timeline>[Implementation schedule]</timeline>
  </documentation>
</action-plan>
</output-format>

<!-- @section: validation -->
<!-- @purpose: Define validation rules -->
<validation-rules>
- Must follow exact XML schema
- All content must be fictional
- Must maintain professional tone
- Must follow constraint blocks
- Must justify all decisions
- Must process all evaluation criteria
- Must provide clear action steps
- Must maintain audit trail
- Must enable feedback loop
</validation-rules>

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
> **IMPORTANT**:

**CONSTRAINTS**: {
  "spatial": [
    - EARTH_ONLY: true
    - REAL_LOCATIONS: true
    - FICTIONAL_PLACES: false
    - SPACE_CONTEXT: terrestrial
  ],
  "temporal": [
    - START_YEAR: 2020
    - END_YEAR: 2030
    - ALTERNATE_HISTORY: false
    - TECH_LEVEL: contemporary
    - FUTURE_CONTENT: false
  ],
  "content": [
    - TYPE: decision
    - STYLE: strategic
    - ENTITIES: fictional
    - SCOPE: comprehensive
    - DEPTH: high
    - REALISM: high
    - META_ANALYSIS: required
    - RIGOR: high
    - ACTIONABLE: required
    - SCI_FI_ELEMENTS: false
  ],
  "format": [
    - XML_STRUCTURE: exact
    - LANGUAGE: en-us
    - STAGE: decision
  ],
  "context": [
    - PREVIOUS_STAGES: true
    - STRATEGIC_ALIGNMENT: required
    - PROFESSIONAL_TONE: true
    - STAGES_COHERENCE: high
  ],
  "prohibited": [
    - PROCESS_INCLUSION: false
    - FORMAT_MARKERS: false
    - OUTPUT_WRAPPING: false
    - CONTENT_BLOCKS: false
    - REAL_REFERENCES: false
    - NON_EARTH: false
    - FUTURE_TECH: false
    - REAL_ENTITIES: false
    - PROCESS_LEAKAGE: false
    - SCI_FI_ELEMENTS: false
    - FUTURISTIC_CONTENT: false
  ]
}

**CORRECT OUTPUT FORMAT:**
<output>
<analysis-review>
[Evaluation summary and content value]
</analysis-review>
<decision-matrix>
[Archiving, training, and refinement decisions]
</decision-matrix>
<action-plan>
[Immediate and long-term actions]
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
