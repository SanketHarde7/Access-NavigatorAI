# Access Navigator AI – Project Documentation

## 1) Preliminary Investigations

Before building this project, we looked at one basic question: *Why is moving inside a stadium difficult for many people with disabilities?*  
To understand this, we reviewed common accessibility pain points in public venues:

- crowded passages and sudden congestion
- confusion in finding elevators, ramps, and accessible washrooms
- lack of clear, real-time guidance for users with different needs
- language barriers and difficulty understanding static signboards

We also explored how existing navigation systems work. Most systems give generic directions, but they do not adapt well to personal accessibility needs.  
This investigation helped us decide that the solution must be **dynamic, personalized, and safety-focused**.

---

## 2) Problem Identification

The core problem is that stadium navigation is not equally usable for everyone.  
People with mobility, visual, or hearing challenges often face extra effort, stress, and risk while moving from one area to another.

Current methods (maps, signs, staff support) are helpful but limited:

- maps are not always easy to read quickly
- signboards do not update based on live crowd conditions
- manual help may not be instantly available during peak times

So, the identified problem is not just “finding a path,” but **finding a safe, accessible, and context-aware path in real time**.

---

## 3) Problem Definition

This project addresses the following defined problem:

> Design a smart assistant that can guide stadium visitors through safe and accessible routes based on their personal needs and live environment conditions.

In simpler words, the system should:

- understand who the user is and what support they need
- check live crowd and zone information
- avoid unsafe or blocked areas
- suggest the best route in clear, easy language

This definition keeps both technology and human usability in focus.

---

## 4) Purpose of the Project

The purpose of Access Navigator AI is to make stadium experiences more inclusive, independent, and stress-free for people with disabilities.

Main purpose points:

- provide personalized navigation instead of one-size-fits-all routes
- improve user safety by considering live conditions
- reduce confusion and decision fatigue in complex stadium layouts
- support better communication with simple, user-friendly responses

Overall, the project aims to build confidence for users so they can move with dignity and less dependency on constant manual help.

---

## 5) Feasibility Study

Before moving to full-scale implementation, we checked whether this project is practical from different angles.

### a) Economic Feasibility

The project is economically feasible for phased deployment.  
The core software stack (React, FastAPI, Python, and open development tooling) is cost-effective.  
Cloud and AI API costs can be controlled by using optimized prompts, route caching, and fallback model strategies.  
Compared to the long-term social value and improved user experience in stadiums, the expected cost is reasonable.

### b) Technical Feasibility

The project is technically feasible because the required technologies are mature and already available.  
The multi-agent architecture, real-time APIs, and accessibility-focused frontend are practical to build with the current stack.  
The system can also scale step by step, starting from pilot stadium environments and then expanding with deeper sensor integration.

### c) Operational Feasibility

The project is operationally feasible for real venue use.  
Users can interact with the assistant in simple language, and support teams can monitor operations through standard backend services.  
The system is designed to assist staff, not replace them, which makes adoption smoother in stadium workflows.

---

## 6) Scope of the Project

The current scope of this project includes:

- AI-based conversational guidance for stadium movement
- route decision support using accessibility and crowd context
- user-centric response generation in understandable language
- multi-agent architecture for perception, reasoning, and communication

What is in scope:

- assisting users during navigation inside stadium areas
- real-time recommendation logic based on available system data
- focus on accessibility-first decision making

What is out of scope (for now):

- full hardware-level integration with every stadium sensor system
- replacing emergency personnel or medical response teams
- universal city-wide navigation beyond stadium boundaries

---

## 7) Limitations

Like any practical system, this project has limitations:

- **Data dependency:** Output quality depends on the quality and freshness of input data.
- **Environment variability:** Real-world stadium conditions can change faster than system updates in some cases.
- **Infrastructure differences:** Not all stadiums have the same accessibility infrastructure or digital readiness.
- **Model interpretation limits:** AI can still make imperfect suggestions if context is incomplete.
- **Internet/system availability:** Service interruptions can impact real-time assistance.

Even with these limitations, the project creates a strong foundation for accessible, intelligent navigation and can improve over time with better data, testing, and deployments.

---

## 8) System Specifications

To run Access Navigator AI smoothly in development and pilot deployment, the following baseline system specifications are recommended.

### Hardware Specifications

- **RAM:** 16 GB minimum (recommended for running frontend, backend, and AI integrations together)
- **Processor:** Intel Core i5 (10th Gen or above) / AMD Ryzen 5 or equivalent
- **Storage:** 512 GB SSD (minimum 20 GB free space for project, dependencies, and logs)
- **Network:** Stable broadband internet (minimum 20 Mbps) for real-time API communication
- **Optional Devices:** Microphone and speaker/headset for voice-based accessibility interactions

### Software Specifications

- **Operating System:** Windows 10/11, Ubuntu 22.04+, or macOS 12+
- **Frontend Runtime:** Node.js 18+ and npm
- **Backend Runtime:** Python 3.11+
- **Backend Framework:** FastAPI with required Python packages from `requirements.txt`
- **Browser Support:** Latest Chrome, Edge, or Firefox for best UI and accessibility support
- **Version Control:** Git (for collaboration and deployment workflows)

---

## 9) Technical Requirements of the System

The system should meet these technical requirements:

- Support a multi-agent AI workflow for perception, reasoning, communication, and conversation handling
- Process user requests with low latency so route guidance feels real time
- Integrate with crowd and zone status inputs to generate safe route suggestions
- Provide secure API communication between frontend and backend services
- Handle multilingual and accessibility-friendly interaction formats where possible
- Offer fault-tolerant behavior (fallback responses) when some live data is missing

---

## 10) Functional Requirements of the System

From a user and operations perspective, the system should:

- Accept user inputs related to destination, mobility needs, and preferences
- Identify safe and accessible paths based on current context
- Avoid restricted, blocked, emergency, or high-risk zones in route suggestions
- Explain directions in clear, simple language
- Update guidance when route conditions change
- Support conversational follow-up questions (for example: alternate path requests)
- Provide responses that are easy to understand for users with different accessibility needs

---

## 11) Data Requirements of the System

For reliable output, the system needs structured and timely data such as:

- Stadium map/graph data (zones, paths, entrances, exits, ramps, elevators, washrooms)
- Live or near-live crowd density and zone condition information
- Accessibility metadata for each path/zone (wheelchair-friendly, low-vision support indicators, etc.)
- Basic user-context data (required assistance preferences and destination intent)
- Safety status data (closed zones, temporary barriers, emergency flags)
- System logs for monitoring, debugging, and service improvement

Data should be validated, updated regularly, and stored with proper access control to maintain quality and trust.
