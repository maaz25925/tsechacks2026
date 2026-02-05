# Postman Automated Testing Guide

## Overview

This guide explains how to set up automated tests in Postman to validate API responses and automatically extract data for use in subsequent requests.

---

## 📊 Test Structure in Postman

Postman tests are written in JavaScript and executed after a request receives a response.

### Where to Add Tests

1. Open any request in Postman
2. Click the **"Tests"** tab (next to "Body")
3. Write your test code
4. Click **Send** - tests run after response

---

## ✅ Testing Authentication Flow

### Test: Login Response

```javascript
// Test: Login returns access token
pm.test("Login should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Login response should have access_token", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("access_token");
    pm.expect(jsonData.access_token).to.be.a("string");
    pm.expect(jsonData.access_token.length).to.be.greaterThan(0);
});

pm.test("Should save access_token to environment", function() {
    let jsonData = pm.response.json();
    pm.environment.set("ACCESS_TOKEN", jsonData.access_token);
});

pm.test("Response should contain user info", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("user_id");
    pm.expect(jsonData).to.have.property("email");
    pm.expect(jsonData).to.have.property("role");
});
```

---

## 🎬 Testing Session Management

### Test: Start Session

```javascript
// Test: Start session returns correct fields
pm.test("Start session should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Response should have required session fields", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("session_id");
    pm.expect(jsonData).to.have.property("status");
    pm.expect(jsonData).to.have.property("reserve_amount");
    pm.expect(jsonData).to.have.property("transaction_id");
});

pm.test("Session ID should have correct format", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.session_id).to.match(/^sess_/);
});

pm.test("Status should be 'active'", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal("active");
});

pm.test("Reserve amount should match request", function() {
    let jsonData = pm.response.json();
    let requestData = JSON.parse(pm.request.body.raw);
    pm.expect(jsonData.reserve_amount).to.equal(requestData.reserve_amount);
});

pm.test("Should save session_id to environment", function() {
    let jsonData = pm.response.json();
    pm.environment.set("SESSION_ID", jsonData.session_id);
});

pm.test("Should save transaction_id to environment", function() {
    let jsonData = pm.response.json();
    pm.environment.set("TRANSACTION_ID", jsonData.transaction_id);
});
```

### Test: End Session

```javascript
// Test: End session calculation
pm.test("End session should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Response should have breakdown fields", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("session_id");
    pm.expect(jsonData).to.have.property("duration_min");
    pm.expect(jsonData).to.have.property("final_amount_charged");
    pm.expect(jsonData).to.have.property("refund_amount");
});

pm.test("Duration should be positive", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.duration_min).to.be.greaterThan(0);
});

pm.test("Charge + refund should equal reserve", function() {
    let jsonData = pm.response.json();
    let total = jsonData.final_amount_charged + jsonData.refund_amount;
    pm.expect(total).to.be.closeTo(jsonData.reserve_amount, 0.01);
});

pm.test("Completion percentage should be 0-100", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.completion_percentage).to.be.at.least(0);
    pm.expect(jsonData.completion_percentage).to.be.at.most(100);
});
```

---

## 💰 Testing Milestone Operations

### Test: Create Payment Intent

```javascript
// Test: Payment intent creation
pm.test("Create intent should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Response should have intent and escrow IDs", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("intent_id");
    pm.expect(jsonData).to.have.property("escrow_id");
    pm.expect(jsonData).to.have.property("status");
    pm.expect(jsonData).to.have.property("total_amount");
});

pm.test("Intent ID should have correct format", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.intent_id).to.match(/^intent_/);
});

pm.test("Escrow ID should have correct format", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.escrow_id).to.match(/^escrow_/);
});

pm.test("Status should be 'active'", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal("active");
});

pm.test("Total amount should match request", function() {
    let jsonData = pm.response.json();
    let requestData = JSON.parse(pm.request.body.raw);
    pm.expect(jsonData.total_amount).to.equal(requestData.amount);
});

pm.test("Should save intent_id and escrow_id", function() {
    let jsonData = pm.response.json();
    pm.environment.set("INTENT_ID", jsonData.intent_id);
    pm.environment.set("ESCROW_ID", jsonData.escrow_id);
});
```

### Test: Create Milestone

```javascript
// Test: Milestone creation
pm.test("Create milestone should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Milestone should have all required fields", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
    pm.expect(jsonData).to.have.property("escrow_id");
    pm.expect(jsonData).to.have.property("session_id");
    pm.expect(jsonData).to.have.property("status");
    pm.expect(jsonData).to.have.property("amount");
    pm.expect(jsonData).to.have.property("percentage");
});

pm.test("Milestone status should be 'pending'", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal("pending");
});

pm.test("Amount should match request", function() {
    let jsonData = pm.response.json();
    let requestData = JSON.parse(pm.request.body.raw);
    pm.expect(jsonData.amount).to.equal(requestData.amount);
});

pm.test("Percentage should match request", function() {
    let jsonData = pm.response.json();
    let requestData = JSON.parse(pm.request.body.raw);
    pm.expect(jsonData.percentage).to.equal(requestData.percentage);
});

pm.test("Percentage should be 0-100", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.percentage).to.be.at.least(0);
    pm.expect(jsonData.percentage).to.be.at.most(100);
});

pm.test("Should save milestone ID", function() {
    let jsonData = pm.response.json();
    pm.environment.set("MILESTONE_ID", jsonData.id);
});
```

### Test: Submit Milestone Proof

```javascript
// Test: Proof submission
pm.test("Submit proof should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Proof response should have completion data", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("milestone_id");
    pm.expect(jsonData).to.have.property("status");
    pm.expect(jsonData).to.have.property("amount_released");
});

pm.test("Status should be 'completed'", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal("completed");
});

pm.test("Amount released should be positive", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.amount_released).to.be.greaterThan(0);
});

pm.test("Should have transaction ID", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("finternet_tx_id");
    pm.expect(jsonData.finternet_tx_id).to.be.a("string");
});
```

---

## 📋 Testing List Operations

### Test: Get Session Milestones

```javascript
// Test: List milestones
pm.test("List milestones should return 200 OK", function() {
    pm.response.to.have.status(200);
});

pm.test("Response should have milestones array", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("milestones");
    pm.expect(jsonData.milestones).to.be.an("array");
});

pm.test("Should have total count", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("total");
    pm.expect(jsonData.total).to.be.a("number");
});

pm.test("Milestones should have correct structure", function() {
    let jsonData = pm.response.json();
    if (jsonData.milestones.length > 0) {
        let milestone = jsonData.milestones[0];
        pm.expect(milestone).to.have.property("id");
        pm.expect(milestone).to.have.property("status");
        pm.expect(milestone).to.have.property("amount");
    }
});

pm.test("All milestones should be from correct session", function() {
    let jsonData = pm.response.json();
    let sessionId = pm.environment.get("SESSION_ID");
    jsonData.milestones.forEach(function(milestone) {
        pm.expect(milestone.session_id).to.equal(sessionId);
    });
});

pm.test("Total should match array length", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.total).to.equal(jsonData.milestones.length);
});
```

---

## 🔒 Testing Error Scenarios

### Test: Insufficient Balance (Expected 402)

```javascript
// Add to "Start Session" request with high reserve
pm.test("Should return 402 for insufficient balance", function() {
    pm.response.to.have.status(402);
});

pm.test("Error message should be clear", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("error");
    pm.expect(jsonData.error).to.have.property("code");
    pm.expect(jsonData.error.code).to.equal("INSUFFICIENT_BALANCE");
});
```

### Test: Invalid Session (Expected 404)

```javascript
// Add to "End Session" request with fake ID
pm.test("Should return 404 for invalid session", function() {
    pm.response.to.have.status(404);
});

pm.test("Error should indicate not found", function() {
    let jsonData = pm.response.json();
    pm.expect(jsonData.error.code).to.equal("SESSION_NOT_FOUND");
});
```

---

## 🔄 Pre-request Scripts

### Validate Environment Variables

```javascript
// Add to any authenticated request's "Pre-request Script" tab

let requiredVars = ["ACCESS_TOKEN", "BASE_URL"];
requiredVars.forEach(function(varName) {
    let value = pm.environment.get(varName);
    if (!value) {
        throw new Error("Required variable not set: " + varName);
    }
});

console.log("✓ All required variables are set");
```

### Add Timestamps

```javascript
// Automatically add current timestamp to requests

pm.environment.set("TIMESTAMP", new Date().toISOString());

// Then use in request body:
// "timestamp": "{{TIMESTAMP}}"
```

### Generate Unique IDs

```javascript
// Generate unique user emails for registration

let timestamp = Date.now();
let uniqueEmail = "user_" + timestamp + "@example.com";
pm.environment.set("UNIQUE_EMAIL", uniqueEmail);

// Then use in registration request:
// "email": "{{UNIQUE_EMAIL}}"
```

---

## 📊 Workflow Test Suite

### Complete Session Workflow Test

```javascript
// Save after each step for debugging
pm.test("Step tracker - Login", function() {
    console.log("✓ Completed: Login");
});

// Later in another request:
pm.test("Step tracker - Start Session", function() {
    console.log("✓ Completed: Start Session");
    console.log("  Session ID: " + pm.environment.get("SESSION_ID"));
});

// Even later:
pm.test("Step tracker - End Session", function() {
    console.log("✓ Completed: End Session");
    let sessionData = pm.response.json();
    console.log("  Duration: " + sessionData.duration_min + " minutes");
    console.log("  Charge: $" + sessionData.final_amount_charged);
    console.log("  Refund: $" + sessionData.refund_amount);
});

// View results in Postman Console: Ctrl+Alt+C (Windows) or Cmd+Alt+C (Mac)
```

---

## 🎯 Best Practices

### Do's ✅
- Use descriptive test names
- Test both happy path and error scenarios
- Validate data types, not just existence
- Use `pm.environment.set()` to save important IDs
- Add console.log for debugging
- Test numeric ranges (e.g., 0-100 for percentages)
- Verify timestamps are valid ISO 8601 format

### Don'ts ❌
- Don't hardcode values (use environment variables)
- Don't test multiple endpoints in one test
- Don't skip negative test cases
- Don't ignore error responses
- Don't create dependencies between test suites

---

## 🚀 Running Tests

### Manual Testing
1. Open request
2. Click **"Tests"** tab, write tests
3. Click **Send**
4. View results in **"Test Results"** tab

### Automated Testing (Collection Runner)
1. Click **"Collections"** in left sidebar
2. Right-click collection → **"Run collection"**
3. Configure environment
4. Click **"Run"**
5. View full test report

### Export Test Results
1. After collection run, click **"Export Results"**
2. Save as JSON or HTML
3. Share with team

---

## 📈 Sample Test Report

```
↳ Murph Backend API
  ↳ Authentication
    POST /auth/login
    ✓ Login should return 200 OK
    ✓ Login response should have access_token
    ✓ Should save access_token to environment
    ✓ Response should contain user info
    
  ↳ Sessions
    POST /sessions/start
    ✓ Start session should return 200 OK
    ✓ Response should have required session fields
    ✓ Session ID should have correct format
    ✓ Status should be 'active'
    ✓ Reserve amount should match request
    ✓ Should save session_id to environment
    
    POST /sessions/end
    ✓ End session should return 200 OK
    ✓ Response should have breakdown fields
    ✓ Duration should be positive
    ✓ Charge + refund should equal reserve
    
  ↳ Milestones
    POST /milestones/intent
    ✓ Create intent should return 200 OK
    ✓ Response should have intent and escrow IDs
    
    POST /milestones/{id}/proof
    ✓ Submit proof should return 200 OK
    ✓ Status should be 'completed'

_____________________________________________
Total Tests: 35 | Passed: 35 | Failed: 0
```

---

## 🐛 Debugging Failed Tests

### View Test Console
1. Bottom of Postman window
2. Look for test output and errors
3. Check variable values:
   ```javascript
   console.log("Current Access Token: " + pm.environment.get("ACCESS_TOKEN"));
   ```

### Common Issues

**Issue**: Test fails on accessing undefined property
```javascript
// ✗ Wrong
let amount = jsonData.amount; // May be undefined

// ✓ Correct  
pm.expect(jsonData).to.have.property("amount");
let amount = jsonData.amount;
```

**Issue**: Status code test fails
```javascript
// Check actual response in Postman, then adjust test
pm.test("Check status", function() {
    console.log("Actual status: " + pm.response.code); // See what you got
    pm.response.to.have.status(200);
});
```

**Issue**: Variable not persisting
```javascript
// Save to environment explicitly
pm.environment.set("KEY", value);

// Verify it was saved
console.log("Saved value: " + pm.environment.get("KEY"));
```

---

## 📚 Resources

- [Postman Test Examples](https://learning.postman.com/docs/writing-scripts/test-scripts/)
- [Chai Assertions](https://www.chaijs.com/api/bdd/)
- [PM API Reference](https://learning.postman.com/docs/writing-scripts/script-references/postman-sandbox-api-reference/)

---

**Last Updated**: February 5, 2026
**Status**: ✅ Ready to Use
