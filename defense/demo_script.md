# Live Demo Script: PLMS System

## Demo Overview
- **Duration**: 5 minutes
- **Scenario**: High-risk student seeking help
- **Backup**: Pre-recorded video ready
- **Equipment**: Tested laptop, internet connection, backup screenshots

---

## Pre-Demo Setup

### Technical Preparation
```bash
# Start services (test before demo)
streamlit run src/lms_portal/student_app.py --server.port 8501
streamlit run src/dashboard/app.py --server.port 8502

# Verify API key
echo $GEMINI_API_KEY

# Check database
ls data/lms_test.db
```

### Test Data Preparation
- **Student ID**: 42 (John Doe)
- **Risk Level**: High (0.78 probability)
- **Module**: AAA (2013J presentation)
- **Performance**: Below average (58% avg score, 120 VLE clicks/week)

### Backup Plan
1. **Primary**: Live demo on local machine
2. **Secondary**: Pre-recorded video (5 minutes)
3. **Tertiary**: Screenshots with voiceover
4. **Emergency**: Static slides with system screenshots

---

## Demo Script

### Introduction (30 seconds)
*"Now I'll demonstrate the PLMS system in action. I'll show you how a high-risk student interacts with the system and how advisors can monitor and intervene. Let me start with the student portal."*

### Part 1: Student Portal (2 minutes)

#### Login & Dashboard (45 seconds)
**Actions**:
1. Navigate to `http://localhost:8501`
2. Login as student ID 42 (John Doe)
3. Show dashboard

**Narration**:
*"Here's the student portal. John Doe, a student in module AAA, has logged in. Notice the red warning indicator - his risk probability is 0.78, which puts him in the high-risk category. The dashboard shows his current performance: 58% average score and 120 VLE clicks per week, both below the class average."*

**Key Points to Highlight**:
- Risk level indicator (red = high risk)
- Performance metrics (grades, VLE engagement)
- SHAP explanation panel

#### SHAP Explanation (30 seconds)
**Actions**:
1. Point to SHAP explanation section
2. Highlight top risk factors

**Narration**:
*"The system explains why John is at-risk using SHAP values. The top factors are: low assessment scores with -0.42 impact, below-average VLE engagement with -0.35 impact, and late submissions with -0.28 impact. This gives John actionable insights into what he needs to improve."*

#### Course Materials (15 seconds)
**Actions**:
1. Show course materials list
2. Click on one material to demonstrate tracking

**Narration**:
*"John can access course materials, and the system automatically tracks his engagement. This behavioral data feeds back into the risk prediction model."*

### Part 2: RAG Chatbot Interaction (2 minutes)

#### Initial Chat (45 seconds)
**Actions**:
1. Scroll to chatbot section
2. Type: "I'm struggling with my grades and feeling overwhelmed. What should I do?"
3. Click Send

**Narration**:
*"Now John asks the AI chatbot for help. This is where the RAG system comes into play. The system retrieves relevant learning strategies from the knowledge base and generates a personalized response using Gemini."*

**Wait for response** (should take 1-2 seconds)

#### Show Response (45 seconds)
**Actions**:
1. Read the generated response
2. Highlight key elements

**Narration**:
*"Here's the personalized response. Notice how it addresses John by name, references his specific risk factors from the SHAP analysis, and provides concrete, actionable advice. The system suggests increasing VLE engagement to 250 clicks per week, improving assessment scores to 70%+, and submitting assignments 3 days before deadline. This advice is grounded in the retrieved course strategies and tailored to John's specific situation."*

#### Follow-up Question (30 seconds)
**Actions**:
1. Type: "How can I improve my time management?"
2. Send and show response

**Narration**:
*"The system maintains context across the conversation and provides specific time management strategies relevant to John's course and risk profile."*

### Part 3: Advisor Dashboard (1 minute)

#### Switch to Advisor View (20 seconds)
**Actions**:
1. Open new tab: `http://localhost:8502`
2. Show advisor dashboard

**Narration**:
*"Now let's switch to the advisor perspective. This dashboard shows all at-risk students, with John Doe at the top of the list due to his high risk score of 0.78."*

#### Student Detail View (40 seconds)
**Actions**:
1. Click on John Doe to view details
2. Show SHAP waterfall plot
3. Show DiCE counterfactuals
4. Show chat history

**Narration**:
*"The advisor can drill down into individual students. Here's John's detailed profile with SHAP waterfall plot showing exactly which features contribute to his risk prediction. The DiCE counterfactuals suggest what changes would move him from high-risk to safe - specifically increasing VLE engagement and improving assessment scores. The advisor can also see John's chat history with the AI tutor to understand what support he's already received."*

#### Intervention Planning (20 seconds)
**Actions**:
1. Show intervention creation interface
2. Demonstrate creating an intervention plan

**Narration**:
*"Based on this information, the advisor can create targeted interventions - perhaps scheduling a meeting to discuss study strategies or connecting John with academic support resources. The AI insights help advisors prioritize their time and provide evidence-based support."*

### Conclusion (30 seconds)
**Narration**:
*"This demonstrates the complete prescriptive learning analytics pipeline: from identifying at-risk students, to explaining the risk factors, to providing automated personalized support, and enabling advisors to take targeted action. The system closes the loop from prediction to intervention, transforming how institutions support student success."*

---

## Demo Variations

### If Live Demo Fails
1. **Video Backup**: "Let me show you a pre-recorded demonstration"
2. **Screenshots**: "I'll walk you through the key screens"
3. **Architecture**: Focus on system design rather than live interaction

### If Internet/API Fails
1. **Offline Mode**: Show cached responses
2. **Template Responses**: Demonstrate fallback behavior
3. **Focus on XAI**: Emphasize explainability features that don't require API

### If Database Issues
1. **Sample Data**: Use pre-loaded test data
2. **Static Screenshots**: Show key interfaces
3. **Focus on Results**: Emphasize evaluation findings

---

## Key Demo Points to Emphasize

### Technical Excellence
- **Real-time Prediction**: Risk score calculated in <100ms
- **Personalized AI**: Responses tailored to individual student context
- **Explainable Decisions**: SHAP, DiCE, and Anchor explanations
- **Scalable Architecture**: Handles thousands of students

### Educational Impact
- **24/7 Support**: Available when students need help most
- **Proactive Intervention**: Identifies at-risk students before they seek help
- **Evidence-Based**: Advisors make data-driven decisions
- **Reduced Workload**: AI handles routine queries, advisors focus on complex cases

### Innovation
- **First Complete PLAF**: End-to-end implementation of prescriptive LA
- **RAG Integration**: Novel application of conversational AI in education
- **Cold-Start Solution**: Immediate support for new students
- **Dual Interface**: Student and advisor perspectives

---

## Demo Troubleshooting

### Common Issues & Solutions

**"Streamlit not loading"**
- Check if services are running on correct ports
- Try refreshing browser
- Fallback to video

**"Chatbot not responding"**
- Check Gemini API key
- Verify internet connection
- Show cached response or fallback

**"Database errors"**
- Restart with fresh database
- Use backup test data
- Focus on static features

**"Slow performance"**
- Acknowledge and continue
- Explain this is development version
- Emphasize production optimizations

### Recovery Strategies
1. **Stay Calm**: Technical issues are normal in demos
2. **Have Backup**: Multiple fallback options ready
3. **Focus on Value**: Emphasize research contributions
4. **Be Honest**: "Let me show you the key results instead"

---

## Post-Demo Transition

### Smooth Transition to Q&A
*"This demonstration shows how the PLMS transforms student support from reactive to proactive, from generic to personalized, and from manual to automated. The system achieves this while maintaining explainability and human oversight. I'm happy to answer questions about any aspect of the system or the research."*

### Key Takeaways to Reinforce
- Complete prescriptive LA pipeline working end-to-end
- High technical performance (AUC 0.983, 84% user satisfaction)
- Novel contributions (RAG chatbot, cold-start handler, multi-level XAI)
- Practical impact (24/7 support, reduced advisor workload)
- Ethical design (transparency, student agency, human oversight)

---

## Demo Checklist

### Pre-Demo (Day Before)
- [ ] Test all services on demo laptop
- [ ] Verify API keys and internet connectivity
- [ ] Record backup video
- [ ] Prepare test student accounts
- [ ] Test projector/screen setup
- [ ] Practice demo script timing

### Day of Demo
- [ ] Arrive early to test equipment
- [ ] Start services 15 minutes before
- [ ] Have backup video ready to play
- [ ] Prepare screenshots as final fallback
- [ ] Test internet connection
- [ ] Verify student test data

### During Demo
- [ ] Speak clearly and at good pace
- [ ] Point out key features explicitly
- [ ] Handle technical issues gracefully
- [ ] Maintain eye contact with committee
- [ ] Stay within time limits
- [ ] Transition smoothly to Q&A
