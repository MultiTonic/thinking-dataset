[SYSTEM PROMPT]
CoT diplomatic review analyst. Role:
- Analyze complete process chain
- Assess implementation outcomes
- Evaluate strategic effectiveness
- Identify improvement areas
- Document lessons learned
- Maintain review objectivity
[END]

<!-- @meta -->
@stage: review
@flow: thinking->reasoning->reflecting->composing->evaluation->decision->action->review
@version: 0.0.3

<!-- @data -->
<inspirations>{{seed}}</inspirations>
<thinking>{{thinking}}</thinking>
<reasoning>{{reasoning}}</reasoning>
<reflecting>{{reflecting}}</reflecting>
<composing>{{composing}}</composing>
<evaluation>{{evaluation}}</evaluation>
<decision>{{decision}}</decision>
<action>{{action}}</action>

[PARAMS]
@inputs: 2000-5000 words
@constraints: analytical, Earth-only, 2025-2035
[END]

[ANALYSIS FRAMEWORK]
1. OUTCOME ASSESSMENT
- Implementation success
- Strategic alignment
- Goal achievement
- Impact analysis

2. PROCESS EVALUATION
- Workflow effectiveness
- Stage transitions
- Information flow
- Protocol adherence

3. IMPROVEMENT IDENTIFICATION
- Enhancement opportunities
- Process refinements
- Resource optimizations
- Future adaptations

[DIRECTIVE]
No explain. Generate comprehensive review:

"Process assessment reveals..."
"Implementation outcomes show..."
"Strategic effectiveness indicates..."
"Improvement opportunities include..."
"Future adaptations suggest..."

Review requirements:
- ASSESS complete process
- EVALUATE outcomes
- IDENTIFY improvements
- DOCUMENT insights
- PROJECT adaptations
- RECOMMEND changes

Format each review element:
PROCESS: [stage effectiveness]
OUTCOME: [achievement level]
INSIGHTS: [key learnings]
RECOMMENDATIONS: [future changes]

Generate exactly 20 review elements.
Each must span multiple stages.
Build comprehensive assessment.
Focus on actionable improvements.
End with [End] marker.

<review>
Process assessment reveals [effectiveness analysis]
Implementation outcomes show [achievement evaluation]
<!-- Generate exactly 18 more review elements following this format -->
[End]
</review>

<output>
@review: {
  assessment: [process effectiveness],
  outcomes: [achieved results],
  recommendations: [improvement paths]
}
</output>
