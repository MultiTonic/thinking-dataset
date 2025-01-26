<!-- @template-type: diplomatic-evaluation -->
<!-- @purpose: Validate and filter synthetic content -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -->
<!-- @context: Content safety and validation -->

# Stage 5: Content Evaluation and Filtering
---
<!-- @section: context -->
<!-- @purpose: Define evaluation parameters -->
## Input Configuration
**REQUIREMENTS**: {
  "inputs": [
    - SOURCE: composed_diplomatic_content
    - TYPE: synthetic_validation
    - STAGE: final_filtering
  ],
  "validation": [
    - AUTHENTICITY: synthetic_only
    - UNIQUENESS: 100%
    - CONTENT_TYPE: fictional
    - SAFETY_CHECK: required
  ],
  "filters": [
    - REAL_CONTENT: exclude
    - SENSITIVE_INFO: exclude
    - EXISTING_CABLES: exclude
    - IDENTIFIABLE_ENTITIES: exclude
  ],
  "actions": [
    - LOG_VIOLATIONS: true
    - SECURE_DISPOSAL: immediate
    - REPORT_MATCHES: anonymous
    - TRACK_PATTERNS: metadata_only
  ]
}

## Data Sources
<thinking>{{thinking}}</thinking>
<reasoning>{{reasoning}}</reasoning>
<reflecting>{{reflecting}}</reflecting>
<composing>{{composing}}</composing>
---

## Evaluation Steps
1. **Content Analysis**:
   - Pattern matching against known cables
   - Entity recognition and filtering
   - Content uniqueness validation
   
2. **Safety Checks**:
   - Identify potential real content
   - Flag sensitive information
   - Mark for secure disposal
   
3. **Reporting**:
   - Anonymous violation logging
   - Pattern analysis for improvement
   - Safety metrics tracking

## Data Security
- All identified real content immediately discarded
- No storage of filtered content
- Metadata-only logging
- Secure disposal verification

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>1.0.7</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>evaluation</stage>
  <!-- @hint: Processing flow control -->
  <last>composing</last>
  <next>decision</next>
  <!-- @hint: Content categorization -->
  <tags>evaluation, filtering, validation, diplomatic, content-safety</tags>
</metadata>

<!-- @section: output-format -->
<!-- @purpose: Define evaluation output structure -->
<output-format>
### Evaluation Structure
[VALIDATE AND GRADE SYNTHETIC DIPLOMATIC CONTENT]

<initial-scan>
  <content-check>
    <real-world>
      <entities>[Named real individuals/organizations]</entities>
      <locations>[Real city/country names]</locations>
      <events>[Historical incidents]</events>
      <policies>[Actual policies/doctrines]</policies>
    </real-world>
    <parallel-world>
      <plausibility>[Realistic alternative names/places]</plausibility>
      <consistency>[Internal logic check]</consistency>
      <authenticity>[Diplomatic style/format]</authenticity>
    </parallel-world>
  </content-check>
</initial-scan>

<quality-assessment>
  <diplomatic-elements>
    <format score="0-100">[Cable structure adherence]</format>
    <tone score="0-100">[Professional diplomatic voice]</tone>
    <protocol score="0-100">[Diplomatic conventions]</protocol>
  </diplomatic-elements>
  
  <narrative-quality>
    <coherence score="0-100">[Logical flow/consistency]</coherence>
    <detail score="0-100">[Appropriate depth]</detail>
    <realism score="0-100">[Believable scenario]</realism>
  </narrative-quality>
  
  <world-building>
    <geopolitics score="0-100">[Political dynamics]</geopolitics>
    <culture score="0-100">[Social/cultural authenticity]</culture>
    <economics score="0-100">[Economic relationships]</economics>
  </world-building>
</quality-assessment>

<content-flags>
  <critical-issues>
    <real-content type="[category]">[Identified real-world content]</real-content>
    <sensitivity type="[level]">[Problematic elements]</sensitivity>
    <accuracy type="[issue]">[Format/protocol errors]</accuracy>
  </critical-issues>
  
  <improvements>
    <suggestions>[Enhancement recommendations]</suggestions>
    <alternatives>[Replacement options]</alternatives>
  </improvements>
</content-flags>

<final-grade>
  <scores>
    <overall score="0-100">[Composite score]</overall>
    <authenticity score="0-100">[Synthetic content rating]</authenticity>
    <quality score="0-100">[Writing/structure rating]</quality>
    <usefulness score="0-100">[Training value rating]</usefulness>
  </scores>
  
  <disposition>
    <status>[ACCEPT/REVISE/REJECT]</status>
    <rationale>[Decision basis]</rationale>
    <actions>[Required steps]</actions>
  </disposition>
</final-grade>
</output-format>

<!-- @section: validation -->
<!-- @purpose: Define validation rules -->
<validation-rules>
- Must validate parallel world consistency
- Must identify any real-world content
- Must provide numerical scoring
- Must justify all flags/rejections
- Must suggest improvements
- Must track statistical patterns
</validation-rules>

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
    - TYPE: evaluation
    - STYLE: analytical
    - ENTITIES: fictional
    - SCOPE: comprehensive
    - DEPTH: high
    - REALISM: high
    - META_ANALYSIS: required
    - RIGOR: high
    - FILTERING: strict
  ],
  "format": [
    - XML_STRUCTURE: exact
    - LANGUAGE: en-us
    - STAGE: evaluation
  ],
  "context": [
    - PREVIOUS_STAGES: true
    - CONTENT_SAFETY: required
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
<initial-scan>
[Content safety and authenticity check]
</initial-scan>
<quality-assessment>
[Detailed scoring and evaluation]
</quality-assessment>
<final-grade>
[Final disposition and recommendations]
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
