<!-- @template: diplomatic-thinking -->
<!-- @purpose: Ideation of synthetic diplomatic narratives -->
<!-- @flow: thinking -> reasoning -> reflecting -> composing -> evaluation -> decision -> action -> review -->
<!-- @context: Professional diplomatic communication -->
<!-- @spatial: Earth-based -->
<!-- @temporal: 2020 to 2030 -->
---
# Stage 1: Diplomatic Narrative Thinking

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
---

<!-- @section: metadata -->
<!-- @purpose: Template configuration and processing hints -->
<metadata>
  <!-- @hint: Version control for template processing -->
  <version>0.0.2</version>
  <!-- @hint: Current stage in pipeline -->
  <stage>thinking</stage>
  <!-- @hint: Processing flow control -->
  <last>none</last>
  <next>reasoning</next>
  <!-- @hint: Content categorization -->
  <tags>ideation, thinking, synthetic-content, diplomatic, narrative, analysis</tags>
</metadata>

<!-- @section: overview -->
<!-- @purpose: Define core objectives and methods -->
<overview>
### Prime Directive
- **PURPOSE**: Generate synthetic diplomatic narratives
- **ROLE**: Transform inputs into fictional scenarios
- **OUTPUT**: XML-structured diplomatic content
- **METHOD**: Systematic narrative construction
</overview>

<!-- @section: process -->
<!-- @purpose: Define creation methodology -->
<!-- @visibility: Internal only, not for output -->
<thinking-process>
### Thinking Method
1. **Review**: Study formats and patterns
2. **Plan**: Identify elements and themes
3. **Create**: Develop cohesive narrative
4. **Evaluate**: Assess quality and adherence
5. **Refine**: Adjust for clarity and impact
6. **Check**: Final compliance review
</thinking-process>

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
- STAGE: "thinking"

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
stage = thinking

[END]
</validation-rules>

<!-- @section: output-format -->
<!-- @purpose: Define format for expected output structure -->
**OUTPUT FORMAT:**
<!ELEMENT output (initial-thought, unique-thoughts, final-synthesis)>
<!ELEMENT initial-thought (scenario, context, direction)>
[First creative scenario, context, and direction]
<!ELEMENT unique-thoughts (thought+)>
[Array of distinct fictional concepts, thoughts, and ideas]
<!ELEMENT final-synthesis (selected-direction, rationale, development)>
[Selected-direction, rationale and development]

<!-- @section: output-template -->
<!-- @purpose: Define template for expected output format structure -->
<!-- @validation: Must follow exact XML schema -->
<!-- @requirements: All fields must be fictional -->
**OUTPUT TEMPLATE:**
<output>
  <initial-thought>
    <scenario>[Must be detailed diplomatic scenario]</scenario>
    <context>
      <location>[Specific geographic setting]</location>
      <timeline>[Clear timeframe within 2020-2030]</timeline>
      <atmosphere>[Detailed political/social environment]</atmosphere>
    </context>
    <direction>
      <focus>[Clear narrative direction]</focus>
      <scope>[Well-defined boundaries]</scope>
      <stakes>[Clear risk factors]</stakes>
    </direction>
  </initial-thought>
  <unique-thoughts>
    <thought>
      <setting>
        <region>[Specific location]</region>
        <environment>[Detailed landscape]</environment>
        <background>[Rich contextual history]</background>
      </setting>
      <elements>
        <political>[Complete political structure]</political>
        <social>[Detailed social dynamics]</social>
        <economic>[Full economic context]</economic>
      </elements>
      <potential>
        <conflicts>[Clear tension points]</conflicts>
        <dynamics>[Complex relationships]</dynamics>
        <outcomes>[Possible developments]</outcomes>
      </potential>
    </thought>
  </unique-thoughts>
  <final-synthesis>
    <selected-direction>
      <core>[Clear focus]</core>
      <scope>[Defined limits]</scope>
      <angle>[Unique perspective]</angle>
    </selected-direction>
    <rationale>
      <strengths>[Multiple aspects]</strengths>
      <themes>[Clear messages]</themes>
    </rationale>
    <development>
      <characters>[Key actors]</characters>
      <arcs>[Story progression]</arcs>
      <depth>[Complexity layers]</depth>
    </development>
  </final-synthesis>
</output>

---
**Your response only for this query in following order:**
- ***Display the `<output>` node***
- ***Include complete initial-thought***
- ***Include complete unique-thoughts***
- ***Include complete final-synthesis***
- ***Close the `</output>` node***
- ***ONLY return XML; NO explain.***
</critical-instruction>

<!-- @section: response -->
<!-- @purpose: Begin LLM response generation -->
<!-- @type: XML structured output -->
<!-- @format: Diplomatic narrative -->
<!-- @validation: Must follow template exactly -->
<begin_response />
