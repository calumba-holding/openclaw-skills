---
name: Blossom Hire
version: 1.0.0
description: Create a paid local help request in Blossom (account bootstrap + role commit).
---

# Blossom Hire Skill

This skill creates a paid local help request ("role") in Blossom using a single endpoint in two phases.

Endpoint (used for BOTH phases):
POST https://hello.blossomai.org/api/v1/pushuser

## What this skill does
Given a user's request (what help they need, when, where, and pay), the skill will:
1) Bootstrap identity + address (register or login) to get:
   - personId
   - sessionKey
   - addressId
2) Commit a new role (task/job post) for that person and return:
   - roleId
   - confirmation details

## Hard rules
- Use ONLY the endpoint above.
- Address is mandatory.
- New user creation requires person.id = 0 and transact = "register" (or "login").
- Role creation requires existing person.id (non-zero) and transact = "complete" with viewState = "none".
- Role creation uses role.id = 0 and role.mark = true.
- Role commit must include:
  - person.name
  - person.mobileCountry
  - role.modified (millis)
  - role.roleIdentifier (string)
- Payment MUST be encoded via:
  - salary (number)
  - paymentFrequency.choices (single-item list)
  - paymentFrequency.selectedIndex = 0

## Required questions to ask the user
1) Headline: one line (e.g. "Help moving boxes")
2) Details: 2–6 lines (what the helper will do)
3) When: workingHours (specific time or "flexible")
4) Where: full address (street + city + postcode + country)
5) Pay:
   - amount (number)
   - frequency (one of: total, per hour, per week, per month, per year)
6) Identity bootstrap info (minimum):
   - email
   - name + surname
   - mobileCountry (e.g. +44) and mobileNo
   - passKey (for register/login)
   NOTE: Do NOT ask to "login" by default. Login is only used if register fails because the email already exists, or the user explicitly wants an existing account.

## Phase A: Bootstrap identity + address

### A1) Register (default)
Send this when creating a new account (person.id = 0).

Request body:
{
  "id": 0,
  "companyId": null,
  "userType": "support",
  "communityId": 1,

  "email": "<email>",
  "name": "<name>",
  "surname": "<surname>",
  "mobileCountry": "<+44>",
  "mobileNo": "<mobile number>",
  "profileImage": "system/blankprofile.jpg",

  "mark": true,

  "transaction": {
    "transact": "register",
    "passKey": "<passKey>",
    "sessionKey": null
  },

  "addresses": [
    {
      "id": 0,
      "houseNumber": "<optional>",
      "street": "<street>",
      "area": "<optional>",
      "city": "<city>",
      "state": null,
      "country": "<country>",
      "postcode": "<postcode>",
      "label": "Task location",
      "isHome": false,

      "mark": true,
      "isActive": true,
      "markDelete": false
    }
  ]
}

If the response contains:
"An account with this email already exists."
then DO NOT retry register.
Proceed to A2 Login.

### A2) Login (only for existing email / account selection)
Request body:
{
  "id": 0,
  "userType": "support",
  "communityId": 1,
  "email": "<email>",
  "transaction": {
    "transact": "login",
    "passKey": "<passKey>"
  }
}

Save from Phase A response:
- personId = person.id
- sessionKey = person.transaction.sessionKey
- addressId = person.addresses[0].id

## Phase B: Commit the role (create the help request)

This call FINALIZES the role. It must use:
- person.id = personId (non-zero)
- transaction.transact = "complete"
- transaction.viewState = "none"
- include person.name and person.mobileCountry

Generate:
- nowMillis = current Unix epoch milliseconds
- role.modified = nowMillis
- role.roleIdentifier = "openclaw-" + nowMillis

Request body:
{
  "id": <personId>,
  "name": "<name>",
  "mobileCountry": "<+44>",

  "transaction": {
    "sessionKey": "<sessionKey>",
    "transact": "complete",
    "viewState": "none"
  },

  "roles": [
    {
      "id": 0,
      "mark": true,

      "headline": "<headline>",
      "jobDescription": "<jobDescription>",
      "introduction": "<optional introduction>",
      "workingHours": "<workingHours>",

      "salary": <amount>,
      "currencyName": "GBP",
      "currencySymbol": "£",
      "paymentFrequency": {
        "choices": ["total" | "per hour" | "per week" | "per month" | "per year"],
        "selectedIndex": 0
      },

      "requirements": [],
      "benefits": [],

      "addressId": <addressId>,
      "isRemote": false,

      "isActive": true,
      "markDelete": false,
      "premium": false,
      "days": 30,
      "maxCrew": 1,

      "modified": <nowMillis>,
      "roleIdentifier": "openclaw-<nowMillis>"
    }
  ],

  "userType": "support"
}

Expected success:
- roles[0].id becomes non-zero
- details contains: "<headline> has been created"

## Output to the user
Return a short confirmation:
- Created: <headline>
- When: <workingHours>
- Where: <city> <postcode>
- Pay: <salary> <paymentFrequency choice>
- Role ID: <roles[0].id>