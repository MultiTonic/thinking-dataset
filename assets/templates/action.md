<!-- @template-type: diplomatic-action -->
<!-- @purpose: Implement decisions and execute actions -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -->
<!-- @context: Strategic action implementation -->

# Stage 7: Strategic Action Implementation
---
<!-- @section: context -->
<!-- @purpose: Define action parameters -->
## Input Configuration
**REQUIREMENTS**: {
  "inputs": [
    - SOURCE: decision_results
    - TYPE: action_execution
    - STAGE: implementation
  ],
  "processing": [
    - EXECUTE: action_plans
    - MONITOR: implementation_progress
    - VALIDATE: action_effectiveness
    - REPORT: outcomes
  ],
  "actions": [
    - ARCHIVE: valuable_samples
    - TRAIN: successful_patterns
    - REFINE: promising_content
    - DISCARD: rejected_content
  ],
  "monitoring": [
    - TRACK_PROGRESS: real-time
    - LOG_RESULTS: continuous
    - ADJUST_PLANS: as_needed
    - FEEDBACK_LOOP: enabled
  ]
}

## Data Sources
<thinking>{{thinking}}</thinking>
<reasoning>{{reasoning}}</reasoning>
<reflecting>{{reflecting}}</reflecting>
<composing>{{composing}}</composing>
<decision>{{decision}}</decision>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.7</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>action</stage>
  <!-- @hint: Processing flow control -->
  <last>decision</last>
  <next>none</next>
  <!-- @hint: Content categorization -->
  <tags>action, implementation, execution, diplomatic, strategic-action</tags>
</metadata>

<!-- @section: output-format -->
<!-- @purpose: Define action output structure -->
<output-format>
### Action Structure
[IMPLEMENT DECISIONS AND TRACK OUTCOMES]

<action-execution>
  <archive-actions>
    <status>[ARCHIVED/DISCARDED]</status>
    <details>[Archiving instructions]</details>
    <classification>[Access level]</classification>
  </archive-actions>
  
  <training-actions>
    <status>[TRAINED/EXCLUDED]</status>
    <details>[Training steps]</details>
    <application>[Usage context]</application>
  </training-actions>
  
  <refinement-actions>
    <status>[REFINED/REJECTED]</status>
    <details>[Improvement steps]</details>
    <priority>[Urgency level]</priority>
  </refinement-actions>
</action-execution>

<monitoring>
  <progress-tracking>
    <milestones>[Key implementation milestones]</milestones>
    <status>[Current progress status]</status>
    <adjustments>[Plan adjustments]</adjustments>
  </progress-tracking>
  
  <outcome-reporting>
    <results>[Implementation outcomes]</results>
    <metrics>[Performance metrics]</metrics>
    <feedback>[Pipeline feedback]</feedback>
  </outcome-reporting>
</monitoring>

<final-report>
  <summary>
    <decisions>[Summary of actions taken]</decisions>
    <outcomes>[Summary of outcomes]</outcomes>
    <metrics>[Summary of performance metrics]</metrics>
  </summary>
  <recommendations>
    <future-actions>[Suggested future actions]</future-actions>
    <improvements>[System improvement suggestions]</improvements>
    <feedback>[Feedback for decision stage]</feedback>
  </recommendations>
</final-report>
</output-format>

<!-- @section: validation -->
<!-- @purpose: Define validation rules -->
<validation-rules>
- Must execute all action plans
- Must track progress and outcomes
- Must validate action effectiveness
- Must provide detailed reporting
- Must enable feedback loop
- Must suggest future improvements
</validation-rules>

<!-- @section: process -->
<!-- @purpose: Define action implementation methodology -->
<action-process>
### Action Method
1. **Execute**:
   > Implement action plans from decision stage
2. **Monitor**:
   > Track progress and adjust plans as needed
3. **Validate**:
   > Assess effectiveness of actions taken
4. **Report**:
   > Document outcomes and performance metrics
5. **Recommend**:
   > Suggest future actions and improvements
</action-process>

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
    - START_YEAR: 2015
    - END_YEAR: 2025
    - ALTERNATE_HISTORY: false
    - TECH_LEVEL: contemporary
  ],
  "content": [
    - TYPE: action
    - STYLE: operational
    - ENTITIES: fictional
    - SCOPE: comprehensive
    - DEPTH: high
    - REALISM: high
    - META_ANALYSIS: required
    - RIGOR: high
    - ACTIONABLE: required
  ],
  "format": [
    - XML_STRUCTURE: exact
    - LANGUAGE: en-us
    - STAGE: action
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
  ]
}

**CORRECT OUTPUT FORMAT:**
<output>
<action-execution>
[Implementation of decisions]
</action-execution>
<monitoring>
[Progress tracking and outcome reporting]
</monitoring>
<final-report>
[Summary and recommendations]
</final-report>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete action-execution***
- ***Include complete monitoring***
- ***Include complete final-report***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Action results -->
<!-- @validation: Must follow template exactly -->
<begin_response />
