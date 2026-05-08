// Backend endpoint used by the Gmail add-on to analyze the currently opened email.
// Replace this URL when the backend/ngrok address changes.
const BACKEND_URL =
  "https://dispense-gutter-citadel.ngrok-free.dev/analyze-email";


// Main Gmail add-on entry point.
// This function runs automatically when the user opens an email in Gmail.
function onGmailMessageOpen(e) {
  try {
    // Gmail provides the currently opened message ID and a temporary access token.
    const messageId = e.gmail.messageId;
    const accessToken = e.gmail.accessToken;

    // Required for Gmail add-ons before reading the currently opened message.
    GmailApp.setCurrentMessageAccessToken(accessToken);

    // Read the full raw MIME content of the email.
    // The backend uses this to inspect headers, sender, links, attachments, and body text.
    const message = GmailApp.getMessageById(messageId);
    const rawEmail = message.getRawContent();

    // Load saved user context from Google Apps Script storage.
    // These values are optional and help personalize checks such as recipient/name matching.
    const userProperties = PropertiesService.getUserProperties();

    const userName =
      userProperties.getProperty("USER_NAME") || "";

    const userEmail =
      userProperties.getProperty("USER_EMAIL") || "";

    // Send the raw email and user context to the backend scoring engine.
    const response = UrlFetchApp.fetch(
      BACKEND_URL,
      {
        method: "post",
        contentType: "application/json",
        muteHttpExceptions: true,
        payload: JSON.stringify({
          raw_email: rawEmail,
          user_name: userName,
          user_email: userEmail,
        }),
      }
    );

    // Validate that the backend returned a successful HTTP response.
    const statusCode = response.getResponseCode();

    if (statusCode < 200 || statusCode >= 300) {
      return buildErrorCard(
        "Backend request failed",
        "Status code: " + statusCode
      );
    }

    // Parse the backend JSON response and render the analysis card.
    const result = JSON.parse(response.getContentText());

    return buildResultCard(result);

  } catch (error) {
    // Show a clean error card instead of crashing the Gmail add-on UI.
    return buildErrorCard(
      "Add-on runtime error",
      String(error)
    );
  }
}


// Builds the main result card that appears inside Gmail after email analysis.
function buildResultCard(result) {
  const verdictConfig = getVerdictConfig(result.verdict);

  const card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("Malicious Mail Analyzer")
        .setSubtitle("Explainable Gmail threat scoring")
    );

  // Top section: verdict, score, and human-readable explanation.
  const verdictSection = CardService.newCardSection();

  verdictSection.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(
          `<b><font color="${verdictConfig.color}">
          ${verdictConfig.icon} ${verdictConfig.label}
          </font></b>`
        )
      )
  );

  verdictSection.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(
          `<b>Maliciousness Score:</b> ${result.regular_score}/100`
        )
      )
  );

  verdictSection.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(verdictConfig.description)
      )
  );

  card.addSection(verdictSection);

  // Add detailed explanation sections below the final verdict.
  addHardSignalsSection(card, result);
  addDetectedFeaturesSection(card, result);
  addSettingsSection(card);

  return card.build();
}


// Adds deterministic/high-confidence security indicators to the card.
// Examples: failed authentication, reply-to mismatch, or risky sender domain.
function addHardSignalsSection(card, result) {
  const section = CardService.newCardSection()
    .setHeader("Hard Signals");

  // If no hard signals exist, show a positive empty-state message.
  if (!result.hard_signals || result.hard_signals.length === 0) {
    section.addWidget(
      CardService.newTextParagraph()
        .setText(
          ltr("No hard security signals detected.")
        )
    );

    card.addSection(section);
    return;
  }

  // Render each hard signal as a separate decorated text item.
  result.hard_signals.forEach(function(signal) {
    section.addWidget(
      CardService.newDecoratedText()
        .setTopLabel(signal.feature_id)
        .setText(
          ltr(
            `<b>${signal.title}</b><br>${signal.description}`
          )
        )
        .setWrapText(true)
    );
  });

  card.addSection(section);
}


// Adds heuristic suspicious indicators detected by the backend.
// These signals contribute to the final maliciousness score.
function addDetectedFeaturesSection(card, result) {
  const section = CardService.newCardSection()
    .setHeader("Detected Signals");

  // If no suspicious features exist, show a clean empty-state message.
  if (!result.detected_features || result.detected_features.length === 0) {
    section.addWidget(
      CardService.newTextParagraph()
        .setText(
          ltr("No suspicious signals detected.")
        )
    );

    card.addSection(section);
    return;
  }

  // Show each suspicious feature with its score contribution and evidence summary.
  result.detected_features.forEach(function(feature) {
    section.addWidget(
      CardService.newDecoratedText()
        .setTopLabel("Score contribution: " + feature.score)
        .setText(
          ltr(
            `<b>${feature.title}</b><br>${feature.description}`
          )
        )
        .setBottomLabel(
          buildEvidenceSummary(feature.evidence)
        )
        .setWrapText(true)
    );
  });

  card.addSection(section);
}


// Adds a settings section so the user can provide personal context.
// This context helps the backend detect impersonation or unusual recipient patterns.
function addSettingsSection(card) {
  const section = CardService.newCardSection()
    .setHeader("User Context");

  section.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(
          "Name and email are used only for personalization and recipient checks."
        )
      )
  );

  section.addWidget(
    CardService.newTextButton()
      .setText("Open settings")
      .setOnClickAction(
        CardService.newAction()
          .setFunctionName("openSettingsCard")
      )
  );

  card.addSection(section);
}


// Opens a separate settings card where the user can save their name and email.
function openSettingsCard() {
  const userProperties = PropertiesService.getUserProperties();

  // Pre-fill the form with existing saved values if they exist.
  const currentName =
    userProperties.getProperty("USER_NAME") || "";

  const currentEmail =
    userProperties.getProperty("USER_EMAIL") || "";

  const card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("User Settings")
        .setSubtitle("Used for personalization analysis")
    );

  const section = CardService.newCardSection();

  section.addWidget(
    CardService.newTextInput()
      .setFieldName("user_name")
      .setTitle("Your name")
      .setValue(currentName)
  );

  section.addWidget(
    CardService.newTextInput()
      .setFieldName("user_email")
      .setTitle("Your email")
      .setValue(currentEmail)
  );

  section.addWidget(
    CardService.newTextButton()
      .setText("Save settings")
      .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
      .setOnClickAction(
        CardService.newAction()
          .setFunctionName("saveSettings")
      )
  );

  card.addSection(section);

  return card.build();
}


// Saves user settings from the settings card into per-user Apps Script storage.
function saveSettings(e) {
  const formInputs = e.commonEventObject.formInputs;

  // Safely extract values from Gmail add-on form inputs.
  const userName =
    getFormInputValue(formInputs, "user_name");

  const userEmail =
    getFormInputValue(formInputs, "user_email");

  const userProperties = PropertiesService.getUserProperties();

  userProperties.setProperty("USER_NAME", userName);
  userProperties.setProperty("USER_EMAIL", userEmail);

  // Show a small notification after successful save.
  return CardService.newActionResponseBuilder()
    .setNotification(
      CardService.newNotification()
        .setText("Settings saved successfully.")
    )
    .build();
}


// Builds a user-friendly error card for backend/API/runtime failures.
function buildErrorCard(title, details) {
  const card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("Malicious Mail Analyzer")
        .setSubtitle("Error")
    );

  const section = CardService.newCardSection();

  section.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(
          // Blue is used here instead of red so the error title matches the add-on design better.
          `<b><font color="#1A73E8">${title}</font></b>`
        )
      )
  );

  section.addWidget(
    CardService.newTextParagraph()
      .setText(
        ltr(details)
      )
  );

  card.addSection(section);

  return card.build();
}


// Converts backend verdict values into UI labels, colors, icons, and explanations.
function getVerdictConfig(verdict) {
  if (verdict === "high_risk") {
    return {
      label: "HIGH RISK",
      color: "#D93025",
      icon: "🔴",
      description:
        "This email contains strong malicious indicators and should be handled with extreme caution."
    };
  }

  if (verdict === "suspicious") {
    return {
      label: "SUSPICIOUS",
      color: "#F29900",
      icon: "🟠",
      description:
        "This email contains suspicious signals. Verify the sender before taking action."
    };
  }

  if (verdict === "low_risk") {
    return {
      label: "LOW RISK",
      color: "#F9AB00",
      icon: "🟡",
      description:
        "This email has minor suspicious indicators but no strong malicious signal."
    };
  }

  // Default verdict when the backend does not return a known risk level.
  return {
    label: "SAFE",
    color: "#188038",
    icon: "🟢",
    description:
      "No meaningful malicious indicators were detected."
  };
}


// Converts backend evidence objects into short readable text for the UI.
function buildEvidenceSummary(evidence) {
  if (!evidence) {
    return "";
  }

  // Evidence for suspicious keyword groups.
  if (evidence.matched_words_by_group) {
    return Object.keys(evidence.matched_words_by_group)
      .map(function(groupName) {
        return groupName + ": " +
          evidence.matched_words_by_group[groupName].join(", ");
      })
      .join(" | ");
  }

  // Evidence for URL/body patterns.
  if (evidence.suspicious_patterns) {
    return "Patterns: " + evidence.suspicious_patterns.join(", ");
  }

  // Evidence for authentication or validation failures.
  if (evidence.failed_checks) {
    return "Failed checks: " + evidence.failed_checks.join(", ");
  }

  // Evidence for risky attachments.
  if (evidence.risky_attachments) {
    return "Risky attachments: " + evidence.risky_attachments.length;
  }

  return "";
}


// Safely extracts a single string value from Apps Script form input data.
function getFormInputValue(formInputs, fieldName) {
  if (
    !formInputs ||
    !formInputs[fieldName] ||
    !formInputs[fieldName].stringInputs ||
    !formInputs[fieldName].stringInputs.value
  ) {
    return "";
  }

  return formInputs[fieldName].stringInputs.value[0] || "";
}


// Forces left-to-right rendering inside Gmail cards.
// This is important because Hebrew Gmail accounts may otherwise display English text incorrectly.
function ltr(text) {
  if (!text) {
    return "";
  }

  return (
    '<div style="direction:ltr;text-align:left;">' +
    text +
    '</div>'
  );
}