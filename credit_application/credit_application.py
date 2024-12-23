from openai import OpenAI
import json

client = OpenAI()

# Sample SOP and Credit Application
sop_text = """
1. Applicant must have a minimum of 3 years in business.
2. Annual revenue must exceed $150,000.
3. Credit limit for first-time applicants should not exceed $20,000.
4. Applicant must have a good or excellent credit history.
5. Collateral is mandatory for all credit exceeding $25,000.
6. Business type must be within the seafood industry.
"""

credit_application = {
    "applicant_name": "Ocean Fresh Seafood Supplies",
    "business_type": "Seafood Retail",
    "annual_revenue": 120000,
    "credit_requested": 30000,
    "credit_history": "Good",
    "years_in_business": 2,
    "collateral_provided": "Yes"
}

# OpenAI API for extracting rules
def extract_rules(sop_text):
    # openai.api_key = "<your_openai_api_key>"  # Replace with your OpenAI key
    prompt = (
        "Extract the rules as structured JSON from the following SOP:\n" + sop_text +
        "\nOutput JSON format: [{'rule_id': 1, 'description': '<rule>', 'condition': '<condition logic>'}, ...]" +
        "Notes:" +
        "\nEnsure each generated condition reflect SOP text syntactically correct." +
        "\nEnsure generated conditions have logical operators as 'or', 'and' and not '||', '&&'" +
        "\nGeneralize the condition to allow multiple acceptable business types" +
        "\nprovide condition text with only credit application keys" + json.dumps(credit_application) +
        "\n sop: 'Collateral is mandatory for all credit exceeding $25,000' should translate to condition 'credit_requested > 25000 and collateral_provided == 'Yes'" +
        "\n Do not generate Business type value like 'etc'" 
        
        
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": prompt},
            ],
    )
    rules = eval(response.choices[0].message.content)
    print(rules)
    return rules

# Dynamically validate rules against the application
def validate_application(rules, application):
    failures = []

    for rule in rules:
        rule_id = rule['rule_id']
        description = rule['description']
        condition = rule['condition']

        try:
            if rule_id == 5:
                print(f"Debug Rule 5: credit_requested = {application.get('credit_requested')}, collateral_provided = {application.get('collateral_provided')}")
            if not eval(condition, {}, application):
                reason = f"Condition '{condition}' evaluated to False with values: " + ", ".join([f"{key}={value}" for key, value in application.items() if key in condition])
                failures.append(f"Rule {rule_id} violated: {description}. Reason: {reason}")
        except Exception as e:
            failures.append(f"Rule {rule_id} could not be evaluated due to error: {str(e)}")

    return failures

# Run the pipeline
if __name__ == "__main__":
    # Step 1: Extract rules from SOP
    rules = extract_rules(sop_text)

    # Step 2: Validate application against rules
    rule_failures = validate_application(rules, credit_application)

    # Output results
    print("Rule Failures:")
    for failure in rule_failures:
        print(failure)
