<!-- @template-type: diplomatic-review -->
<!-- @purpose: Review outcomes and gather feedback -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Strategic review and feedback -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2020 to 2030 -->

# Stage 8: Review and Feedback
---
<!-- @section: context -->
<!-- @purpose: Define review parameters -->
## Input Configuration
[REQUIREMENTS]
> @inputs:
- SOURCE: action results
- TYPE: review and feedback
- STAGE: final review
- STYLE: analytical assessment

> @processing:
- REVIEW: outcomes and effectiveness
- GATHER: stakeholder feedback
- ANALYZE: feedback and insights
- REPORT: findings and recommendations

> @actions:
- DOCUMENT: findings and feedback
- UPDATE: processes and workflows
- TRAIN: team members
- COMMUNICATE: results to stakeholders

> @feedback:
- TRACK METRICS: continuous
- LOG IMPROVEMENTS: required
- MAINTAIN HISTORY: enabled
- UPDATE PIPELINE: as needed
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
<!-- @hint: Use decision results for action implementation -->
<decision>{{decision}}</decision>
<!-- @hint: Use action results for review -->
<action>{{action}}</action>
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.8</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>review</stage>
  <!-- @hint: Processing flow control -->
  <last>action</last>
  <next>none</next>
  <!-- @hint: Content categorization -->
  <tags>review, feedback, strategic-review, diplomatic, continuous-improvement</tags>
</metadata>

<!-- @section: overview -->
<!-- @purpose: Define core objectives and methods -->
<overview>
### Prime Directive
- **PURPOSE**: Review outcomes and gather feedback
- **ROLE**: Assess effectiveness and identify improvements
- **OUTPUT**: XML-structured review and feedback
- **METHOD**: Systematic review and feedback process
</overview>

<!-- @section: process -->
<!-- @purpose: Define review methodology -->
<review-process>
### Review Method
1. **Review**:
   > Assess outcomes and effectiveness of actions
2. **Gather**:
   > Collect feedback from stakeholders
3. **Analyze**:
   > Analyze feedback and identify key insights
4. **Report**:
   > Document findings and recommendations
5. **Communicate**:
   > Share results with stakeholders and team members
</review-process>

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
- TYPE: "review"
- STYLE: "analytical"
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
- STAGE: "review"

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
stage = review

[END]
</validation-rules>

<!-- @section: output-format -->
<!-- @purpose: Define expected output structure -->
**CORRECT OUTPUT FORMAT:**
<!ELEMENT output (review-summary, final-report)>
<!ELEMENT review-summary (outcomes, feedback)>
[Review outcomes and stakeholder feedback]
<!ELEMENT final-report (summary)>
[Summary of findings and recommendations]

<!-- @section: output-example -->
<!-- @purpose: Define expected output structure -->
<!-- @validation: Must follow exact XML schema -->
<!-- @requirements: All fields must be fictional -->
**PROPER STRUCTURE EXAMPLE:**
<output>
  <review-summary>
    <outcomes>
      <effectiveness>[Action effectiveness analysis]</effectiveness>
      <challenges>[Implementation challenges]</challenges>
      <successes>[Key achievements]</successes>
    </outcomes>
    <feedback>
      <stakeholder>
        <responses>[Stakeholder input]</responses>
        <concerns>[Key issues raised]</concerns>
        <suggestions>[Improvement ideas]</suggestions>
      </stakeholder>
      <insights>
        <patterns>[Identified patterns]</patterns>
        <lessons>[Key learnings]</lessons>
        <opportunities>[Growth areas]</opportunities>
      </insights>
      <recommendations>
        <process>[Process improvements]</process>
        <workflow>[Workflow adjustments]</workflow>
        <training>[Training needs]</training>
      </recommendations>
    </feedback>
  </review-summary>
  <final-report>
    <summary>
      <findings>
        <major>[Key findings]</major>
        <minor>[Supporting observations]</minor>
        <impacts>[Identified effects]</impacts>
      </findings>
      <recommendations>
        <strategic>[Long-term changes]</strategic>
        <tactical>[Immediate adjustments]</tactical>
        <resource>[Resource needs]</resource>
      </recommendations>
      <next-steps>
        <immediate>[Priority actions]</immediate>
        <planned>[Scheduled improvements]</planned>
        <contingent>[Conditional steps]</contingent>
      </next-steps>
    </summary>
  </final-report>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete review-summary***
- ***Include complete final-report***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Review results -->
<!-- @validation: Must follow template exactly -->
<begin_response />
