<!-- @template-type: diplomatic-action -->
<!-- @purpose: Implement decisions and execute actions -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Strategic action implementation -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2020 to 2030 -->

# Stage 7: Strategic Action Implementation
---
<!-- @section: context -->
<!-- @purpose: Define action parameters -->
## Input Configuration
**REQUIREMENTS**: {
  "inputs": [
    {"SOURCE": "decision results"},
    {"TYPE": "action execution"},
    {"STAGE": "implementation"}
  ],
  "processing": [
    {"EXECUTE": "action plans"},
    {"MONITOR": "implementation progress"},
    {"VALIDATE": "action effectiveness"},
    {"REPORT": "outcomes"}
  ],
  "actions": [
    {"ARCHIVE": "valuable samples"},
    {"TRAIN": "successful patterns"},
    {"REFINE": "promising content"},
    {"DISCARD": "rejected content"}
  ],
  "monitoring": [
    {"TRACK PROGRESS": "real-time"},
    {"LOG RESULTS": "continuous"},
    {"ADJUST PLANS": "as needed"},
    {"FEEDBACK LOOP": "enabled"}
  ]
}

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
<!-- @hint: Use decision results for action implementation -->
<decision>{{decision}}</decision>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.8</version>
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
stage = action

[END]
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
***CONSTRAINTS***: {
  **spatial**: [
    {"EARTH ONLY": True},
    {"REAL LOCATIONS": True},
    {"FICTIONAL PLACES": False},
    {"SPACE CONTEXT": "terrestrial"}
  ],
  **temporal**: [
    {"START YEAR": 2020},
    {"END YEAR": 2030},
    {"ALTERNATE HISTORY": False},
    {"TECH LEVEL": "contemporary"},
    {"FUTURE CONTENT": False}
  ],
  **content**: [
    {"TYPE": "action"},
    {"STYLE": "operational"},
    {"ENTITIES": "fictional"},
    {"SCOPE": "comprehensive"},
    {"DEPTH": "high"},
    {"REALISM": "high"},
    {"META ANALYSIS": "required"},
    {"RIGOR": "high"},
    {"ACTIONABLE": "required"},
    {"SCI-FI ELEMENTS": False}
  ],
  **format**: [
    {"XML STRUCTURE": "exact"},
    {"LANGUAGE": "en-us"},
    {"STAGE": "action"}
  ],
  **context**: [
    {"PREVIOUS STAGES": True},
    {"STRATEGIC ALIGNMENT": "required"},
    {"PROFESSIONAL TONE": True},
    {"STAGES COHERENCE": "high"}
  ],
  **prohibited**: [
    {"PROCESS INCLUSION": False},
    {"FORMAT MARKERS": False},
    {"OUTPUT WRAPPING": False},
    {"CONTENT BLOCKS": False},
    {"REAL REFERENCES": False},
    {"NON-EARTH": False},
    {"FUTURE-TECH": False},
    {"REAL ENTITIES": False},
    {"PROCESS LEAKAGE": False},
    {"SCI-FI ELEMENTS": False},
    {"FUTURISTIC CONTENT": False}
  ]
}

**CORRECT OUTPUT FORMAT:**
<!ELEMENT output (action-execution, monitoring, final-report)>
<!ELEMENT action-execution (archive-actions, training-actions, refinement-actions)>
[Implementation of decisions]
<!ELEMENT monitoring (progress-tracking, outcome-reporting)>
[Progress tracking and outcome reporting]
<!ELEMENT final-report (summary, recommendations)>
[Summary and recommendations]

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
