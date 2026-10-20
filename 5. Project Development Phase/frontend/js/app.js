/**
 * Multimodal Attendance & Engagement Agent - Frontend Client Controller
 * Complete Integration for Technical Architecture, 15 Instructions, AI Service Layer & Edge Storage
 */

class DashboardController {
  constructor() {
    this.telemetryHistory = [];
    this.maxHistoryPoints = 60;
    this.isPrivacyBlurEnabled = true;
    this.eventSource = null;
    this.canvas = document.getElementById("engagementCanvas");
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;

    // Web Audio State
    this.audioContext = null;
    this.analyser = null;
    this.micStream = null;
    this.micInterval = null;
    this.isLiveMicActive = false;

    this.initElements();
    this.bindEvents();
    this.startTelemetryStream();
    this.startRosterPolling();
    this.startChartRendering();
    this.loadInitialInstructions();
  }

  initElements() {
    // Top Nav
    this.sessionTimer = document.getElementById("sessionTimer");
    this.privacyBtnText = document.getElementById("privacyBtnText");
    this.togglePrivacyBtn = document.getElementById("togglePrivacyBtn");
    this.videoSourceSelect = document.getElementById("videoSourceSelect");
    this.audioSourceSelect = document.getElementById("audioSourceSelect");
    this.exportCsvBtn = document.getElementById("exportCsvBtn");
    this.resetSessionBtn = document.getElementById("resetSessionBtn");
    this.privacyWatermark = document.getElementById("privacyWatermark");
    this.blurIndicatorTag = document.getElementById("blurIndicatorTag");
    this.audioModeTag = document.getElementById("audioModeTag");

    // Modal Trigger Buttons
    this.openArchitectureBtn = document.getElementById("openArchitectureBtn");
    this.openLogsBtn = document.getElementById("openLogsBtn");
    this.openFusionBtn = document.getElementById("openFusionBtn");
    this.openStorageBtn = document.getElementById("openStorageBtn");
    this.openTestsBtn = document.getElementById("openTestsBtn");
    this.viewLogsRosterBtn = document.getElementById("viewLogsRosterBtn");
    this.openAudioAnalysisBtn = document.getElementById("openAudioAnalysisBtn");
    this.openMultimodalAgentBtn = document.getElementById("openMultimodalAgentBtn");
    this.openFusionActivityBtn = document.getElementById("openFusionActivityBtn");
    this.openScoringActivityBtn = document.getElementById("openScoringActivityBtn");
    this.openRecommendationsBtn = document.getElementById("openRecommendationsBtn");
    this.openStudentAnalyticsBtn = document.getElementById("openStudentAnalyticsBtn");

    // Activity 5.1 Teaching Suggestion Logic Modal Elements
    this.recommendationsModal = document.getElementById("recommendationsModal");
    this.recTeacherName = document.getElementById("recTeacherName");
    this.recEffectivenessScore = document.getElementById("recEffectivenessScore");
    this.recEffectivenessTrend = document.getElementById("recEffectivenessTrend");
    this.recClassHistoryList = document.getElementById("recClassHistoryList");
    this.recStudentTrendsList = document.getElementById("recStudentTrendsList");
    this.recStrengthsList = document.getElementById("recStrengthsList");
    this.recCountBadge = document.getElementById("recCountBadge");
    this.recommendationsFeedList = document.getElementById("recommendationsFeedList");

    // Activity 5.2 Student Session Analytics Modal Elements
    this.studentAnalyticsModal = document.getElementById("studentAnalyticsModal");
    this.studentSelectActivity52 = document.getElementById("studentSelectActivity52");
    this.stuAttStatusBadge = document.getElementById("stuAttStatusBadge");
    this.stuActiveDuration = document.getElementById("stuActiveDuration");
    this.stuPresenceRatio = document.getElementById("stuPresenceRatio");
    this.stuFirstSeen = document.getElementById("stuFirstSeen");
    this.stuAuditProof = document.getElementById("stuAuditProof");
    this.stuConsistencyBadge = document.getElementById("stuConsistencyBadge");
    this.stuConsistencyScore = document.getElementById("stuConsistencyScore");
    this.stuConsistencyDesc = document.getElementById("stuConsistencyDesc");
    this.stuBarHighFocus = document.getElementById("stuBarHighFocus");
    this.stuBarBalanced = document.getElementById("stuBarBalanced");
    this.stuBarDistraction = document.getElementById("stuBarDistraction");
    this.stuHighFocusPct = document.getElementById("stuHighFocusPct");
    this.stuBalancedPct = document.getElementById("stuBalancedPct");
    this.stuDistractPct = document.getElementById("stuDistractPct");
    this.stuFocusPeriodsList = document.getElementById("stuFocusPeriodsList");
    this.stuNotableTrendsList = document.getElementById("stuNotableTrendsList");
    this.stuPrimaryTakeaway = document.getElementById("stuPrimaryTakeaway");
    this.stuQuestionsList = document.getElementById("stuQuestionsList");
    this.stuCohortTableBody = document.getElementById("stuCohortTableBody");

    // Activity 4.3 Engagement Scoring Modal Elements
    this.scoringActivityModal = document.getElementById("scoringActivityModal");
    this.scoringCompositeVal = document.getElementById("scoringCompositeVal");
    this.scoringTierBadge = document.getElementById("scoringTierBadge");
    this.scoringStabilityVal = document.getElementById("scoringStabilityVal");
    this.scoringFlucIndex = document.getElementById("scoringFlucIndex");
    this.scoringPeaksCount = document.getElementById("scoringPeaksCount");
    this.scoringDisengageCount = document.getElementById("scoringDisengageCount");
    this.scoringDominantDriver = document.getElementById("scoringDominantDriver");
    this.scoringVisScore = document.getElementById("scoringVisScore");
    this.scoringVisContrib = document.getElementById("scoringVisContrib");
    this.scoringVisWeight = document.getElementById("scoringVisWeight");
    this.scoringMotScore = document.getElementById("scoringMotScore");
    this.scoringMotContrib = document.getElementById("scoringMotContrib");
    this.scoringMotWeight = document.getElementById("scoringMotWeight");
    this.scoringInaScore = document.getElementById("scoringInaScore");
    this.scoringInaContrib = document.getElementById("scoringInaContrib");
    this.scoringInaWeight = document.getElementById("scoringInaWeight");
    this.scoringAudScore = document.getElementById("scoringAudScore");
    this.scoringAudContrib = document.getElementById("scoringAudContrib");
    this.scoringAudWeight = document.getElementById("scoringAudWeight");
    this.temporalProfileChartContainer = document.getElementById("temporalProfileChartContainer");
    this.activePresetBadge = document.getElementById("activePresetBadge");
    this.inputWeightVis = document.getElementById("inputWeightVis");
    this.valWeightVis = document.getElementById("valWeightVis");
    this.inputWeightMot = document.getElementById("inputWeightMot");
    this.valWeightMot = document.getElementById("valWeightMot");
    this.inputWeightIna = document.getElementById("inputWeightIna");
    this.valWeightIna = document.getElementById("valWeightIna");
    this.inputWeightAud = document.getElementById("inputWeightAud");
    this.valWeightAud = document.getElementById("valWeightAud");
    this.scoringPeaksList = document.getElementById("scoringPeaksList");
    this.scoringDisengagementsList = document.getElementById("scoringDisengagementsList");

    // Activity 4.2 Multimodal Signal Fusion Modal Elements
    this.fusionActivityModal = document.getElementById("fusionActivityModal");
    this.fusionSyncJitter = document.getElementById("fusionSyncJitter");
    this.fusionCrossCorr = document.getElementById("fusionCrossCorr");
    this.fusionCoherence = document.getElementById("fusionCoherence");
    this.fusionDominantModality = document.getElementById("fusionDominantModality");
    this.fusionMovementPattern = document.getElementById("fusionMovementPattern");
    this.fusionVisualAttention = document.getElementById("fusionVisualAttention");
    this.fusionPresenceDuration = document.getElementById("fusionPresenceDuration");
    this.fusionMotionEnergy = document.getElementById("fusionMotionEnergy");
    this.fusionInactivitySec = document.getElementById("fusionInactivitySec");
    this.fusionVisContrib = document.getElementById("fusionVisContrib");
    this.fusionSpeechState = document.getElementById("fusionSpeechState");
    this.fusionNoiseSpl = document.getElementById("fusionNoiseSpl");
    this.fusionRhythmState = document.getElementById("fusionRhythmState");
    this.fusionPartFreq = document.getElementById("fusionPartFreq");
    this.fusionSpeakerTurns = document.getElementById("fusionSpeakerTurns");
    this.fusionAudContrib = document.getElementById("fusionAudContrib");
    this.aiSuggestionsContainer = document.getElementById("aiSuggestionsContainer");
    this.fusionCustomModalitiesList = document.getElementById("fusionCustomModalitiesList");

    // Activity 4.1 Multimodal Agent Modal Elements
    this.multimodalAgentModal = document.getElementById("multimodalAgentModal");
    this.agentModalEiValue = document.getElementById("agentModalEiValue");
    this.agentModalStatePill = document.getElementById("agentModalStatePill");
    this.agentModalTrendPill = document.getElementById("agentModalTrendPill");
    this.agentModalDominantModality = document.getElementById("agentModalDominantModality");
    this.agentModalConfidenceBadge = document.getElementById("agentModalConfidenceBadge");
    this.agentModalRuleId = document.getElementById("agentModalRuleId");
    this.agentModalDiagnosisText = document.getElementById("agentModalDiagnosisText");
    this.agentModalVisFactor = document.getElementById("agentModalVisFactor");
    this.agentModalMotFactor = document.getElementById("agentModalMotFactor");
    this.agentModalAudFactor = document.getElementById("agentModalAudFactor");
    this.agentModalModelBadge = document.getElementById("agentModalModelBadge");
    this.agentModalLlmInsightText = document.getElementById("agentModalLlmInsightText");
    this.agentModalLlmRecommendationText = document.getElementById("agentModalLlmRecommendationText");

    // Activity 3.2 Modal & Telemetry Elements
    this.audioAnalysisModal = document.getElementById("audioAnalysisModal");
    this.closeAudioAnalysisModal = document.getElementById("closeAudioAnalysisModal");
    this.modalToggleMicBtn = document.getElementById("modalToggleMicBtn");
    this.audioModalSpl = document.getElementById("audioModalSpl");
    this.audioModalSplBar = document.getElementById("audioModalSplBar");
    this.audioModalDbfs = document.getElementById("audioModalDbfs");
    this.audioModalAmbientLevel = document.getElementById("audioModalAmbientLevel");
    this.audioModalTrend = document.getElementById("audioModalTrend");
    this.audioModalNoiseFloor = document.getElementById("audioModalNoiseFloor");
    this.audioModalQuality = document.getElementById("audioModalQuality");
    this.audioModalSignalStateBadge = document.getElementById("audioModalSignalStateBadge");
    this.audioModalRhythm = document.getElementById("audioModalRhythm");
    this.audioModalVad = document.getElementById("audioModalVad");
    this.audioModalZcr = document.getElementById("audioModalZcr");
    this.audioModalSpectralCentroid = document.getElementById("audioModalSpectralCentroid");
    this.audioModalSpectralFlatness = document.getElementById("audioModalSpectralFlatness");
    this.audioModalDynamicRange = document.getElementById("audioModalDynamicRange");
    this.audioModalSpeechRatio = document.getElementById("audioModalSpeechRatio");
    this.audioModalInteractionIntensity = document.getElementById("audioModalInteractionIntensity");
    this.audioModalParticipationFrequency = document.getElementById("audioModalParticipationFrequency");
    this.audioModalSpeakerTurns = document.getElementById("audioModalSpeakerTurns");
    this.audioModalSpeechPct = document.getElementById("audioModalSpeechPct");
    this.audioModalSilencePct = document.getElementById("audioModalSilencePct");
    this.audioModalNoisePct = document.getElementById("audioModalNoisePct");
    this.audioModalMeanPeak = document.getElementById("audioModalMeanPeak");

    // Modals
    this.architectureModal = document.getElementById("architectureModal");
    this.closeArchitectureModal = document.getElementById("closeArchitectureModal");
    this.tabArchDiagram = document.getElementById("tabArchDiagram");
    this.tabInstructionsList = document.getElementById("tabInstructionsList");
    this.archDiagramView = document.getElementById("archDiagramView");
    this.instructionsListView = document.getElementById("instructionsListView");
    this.instructionsTableBody = document.getElementById("instructionsTableBody");

    this.logsModal = document.getElementById("logsModal");
    this.closeLogsModal = document.getElementById("closeLogsModal");
    this.attendanceLogsTableBody = document.getElementById("attendanceLogsTableBody");
    this.downloadCsvModalBtn = document.getElementById("downloadCsvModalBtn");
    this.downloadJsonModalBtn = document.getElementById("downloadJsonModalBtn");
    this.logsTotalCount = document.getElementById("logsTotalCount");

    this.fusionModal = document.getElementById("fusionModal");
    this.closeFusionModal = document.getElementById("closeFusionModal");
    this.sliderWeightVisual = document.getElementById("sliderWeightVisual");
    this.sliderWeightMotion = document.getElementById("sliderWeightMotion");
    this.sliderWeightAudio = document.getElementById("sliderWeightAudio");
    this.valWeightVisual = document.getElementById("valWeightVisual");
    this.valWeightMotion = document.getElementById("valWeightMotion");
    this.valWeightAudio = document.getElementById("valWeightAudio");
    this.sliderMinSustained = document.getElementById("sliderMinSustained");
    this.sliderSustainedRatio = document.getElementById("sliderSustainedRatio");
    this.sliderWalkbySeconds = document.getElementById("sliderWalkbySeconds");
    this.valMinSustained = document.getElementById("valMinSustained");
    this.valSustainedRatio = document.getElementById("valSustainedRatio");
    this.valWalkbySeconds = document.getElementById("valWalkbySeconds");
    this.saveFusionWeightsBtn = document.getElementById("saveFusionWeightsBtn");

    this.storageModal = document.getElementById("storageModal");
    this.closeStorageModal = document.getElementById("closeStorageModal");
    this.tabStorageAudio = document.getElementById("tabStorageAudio");
    this.tabStorageCode = document.getElementById("tabStorageCode");
    this.tabStorageUploads = document.getElementById("tabStorageUploads");
    this.storageAudioView = document.getElementById("storageAudioView");
    this.storageCodeView = document.getElementById("storageCodeView");
    this.storageUploadsView = document.getElementById("storageUploadsView");
    this.audioFileList = document.getElementById("audioFileList");
    this.codeFileList = document.getElementById("codeFileList");
    this.uploadsFileList = document.getElementById("uploadsFileList");
    this.generateNewAudioBtn = document.getElementById("generateNewAudioBtn");
    this.generateAuditCodeBtn = document.getElementById("generateAuditCodeBtn");
    this.generateTrendCodeBtn = document.getElementById("generateTrendCodeBtn");
    this.triggerUploadBtn = document.getElementById("triggerUploadBtn");
    this.fileUploadInput = document.getElementById("fileUploadInput");

    this.testsModal = document.getElementById("testsModal");
    this.closeTestsModal = document.getElementById("closeTestsModal");
    this.executeTestsBtn = document.getElementById("executeTestsBtn");
    this.testTotalCount = document.getElementById("testTotalCount");
    this.testPassedStatus = document.getElementById("testPassedStatus");
    this.testDurationNum = document.getElementById("testDurationNum");
    this.testOutputLog = document.getElementById("testOutputLog");

    this.visualAidModal = document.getElementById("visualAidModal");
    this.closeVisualAidModal = document.getElementById("closeVisualAidModal");
    this.visualAidSvgContainer = document.getElementById("visualAidSvgContainer");
    this.visualAidTitle = document.getElementById("visualAidTitle");
    this.quickVisualAidBtn = document.getElementById("quickVisualAidBtn");
    this.triggerVisualAidModalBtn = document.getElementById("triggerVisualAidModalBtn");

    // AI & Voice Action Triggers
    this.triggerGeminiBtn = document.getElementById("triggerGeminiBtn");
    this.triggerTtsAlertBtn = document.getElementById("triggerTtsAlertBtn");
    this.quickTtsBtn = document.getElementById("quickTtsBtn");

    // KPIs
    this.engagementIndexValue = document.getElementById("engagementIndexValue");
    this.engagementProgressBar = document.getElementById("engagementProgressBar");
    this.engagementTrendBadge = document.getElementById("engagementTrendBadge");

    this.visualAttentionValue = document.getElementById("visualAttentionValue");
    this.visualProgressBar = document.getElementById("visualProgressBar");
    this.dormantCountSubtext = document.getElementById("dormantCountSubtext");

    this.acousticRhythmValue = document.getElementById("acousticRhythmValue");
    this.audioEnergyBar = document.getElementById("audioEnergyBar");
    this.monologueDurationSubtext = document.getElementById("monologueDurationSubtext");

    this.presentRatioValue = document.getElementById("presentRatioValue");
    this.attendanceProgressBar = document.getElementById("attendanceProgressBar");
    this.attendanceRateBadge = document.getElementById("attendanceRateBadge");

    // Feeds
    this.agentFeed = document.getElementById("agentFeed");
    this.rosterTableBody = document.getElementById("rosterTableBody");

    // Hybrid Enrollment Modal Elements
    this.identifyModal = document.getElementById("identifyModal");
    this.identifyTrackBadge = document.getElementById("identifyTrackBadge");
    this.identifyModalTrackId = document.getElementById("identifyModalTrackId");
    this.identifyFaceCropImg = document.getElementById("identifyFaceCropImg");
    this.identifyFaceCropFallback = document.getElementById("identifyFaceCropFallback");
    this.existingStudentSelect = document.getElementById("existingStudentSelect");
    this.newStudentId = document.getElementById("newStudentId");
    this.newStudentName = document.getElementById("newStudentName");
    this.newStudentSeat = document.getElementById("newStudentSeat");
    this.newStudentPhotoUpload = document.getElementById("newStudentPhotoUpload");
    this.identifyStatusBanner = document.getElementById("identifyStatusBanner");
    this.btnSubmitIdentity = document.getElementById("btnSubmitIdentity");
    this.tabLinkExisting = document.getElementById("tabLinkExisting");
    this.tabEnrollNew = document.getElementById("tabEnrollNew");
    this.sectionLinkExisting = document.getElementById("sectionLinkExisting");
    this.sectionEnrollNew = document.getElementById("sectionEnrollNew");
    this.identifyMode = "existing";
    this.activeIdentifyTrackId = null;
  }

  bindEvents() {
    // 1. Privacy Toggle
    this.togglePrivacyBtn.addEventListener("click", async () => {
      this.isPrivacyBlurEnabled = !this.isPrivacyBlurEnabled;
      try {
        const res = await fetch(`/api/config/privacy?enabled=${this.isPrivacyBlurEnabled}`, { method: "POST" });
        const data = await res.json();
        this.updatePrivacyUI(data.privacy_blur);
      } catch (err) {
        console.error("Error toggling privacy:", err);
      }
    });

    // 2. Video Source Switch
    this.videoSourceSelect.addEventListener("change", async (e) => {
      const source = e.target.value;
      try {
        let url = `/api/config/source?source=${source}`;
        if (source === "file") {
          url += `&video_path=storage/uploads/classroom_lecture_sample.mp4`;
        }
        await fetch(url, { method: "POST" });
        const streamImg = document.getElementById("classroomStream");
        if (streamImg) streamImg.src = `/api/video_feed?t=${Date.now()}`;
        const modalBadge = document.getElementById("activeSourceBadgeModal");
        if (modalBadge) modalBadge.textContent = source.toUpperCase();
      } catch (err) {
        console.error("Error changing video source:", err);
      }
    });

    // 3. Audio Source Switch (Simulated vs Live Browser Mic)
    this.audioSourceSelect.addEventListener("change", async (e) => {
      const mode = e.target.value;
      if (mode === "live_mic") {
        await this.startLiveMicrophone();
      } else {
        this.stopLiveMicrophone();
      }
      try {
        await fetch(`/api/config/audio_source?mode=${mode}`, { method: "POST" });
        this.audioModeTag.textContent = mode === "live_mic" ? "Audio: Live Mic (Active)" : "Audio: Simulated";
      } catch (err) {
        console.error("Error switching audio source:", err);
      }
    });

    // 4. Export CSV
    this.exportCsvBtn.addEventListener("click", () => {
      window.location.href = "/api/attendance/export";
    });
    this.downloadCsvModalBtn.addEventListener("click", () => {
      window.location.href = "/api/attendance/export";
    });
    this.downloadJsonModalBtn.addEventListener("click", () => {
      window.location.href = "/api/attendance/export_json";
    });

    // 5. Reset Session
    this.resetSessionBtn.addEventListener("click", async () => {
      if (confirm("Reset current classroom session? This clears attendance logs and initializes a new audit trail.")) {
        try {
          await fetch("/api/session/reset", { method: "POST" });
          this.telemetryHistory = [];
          this.fetchLiveRoster();
        } catch (err) {
          console.error("Error resetting session:", err);
        }
      }
    });

    // 6. Architecture & 15 Instructions Modal
    this.openArchitectureBtn.addEventListener("click", () => this.openArchitectureModal());
    this.closeArchitectureModal.addEventListener("click", () => this.closeArchitectureModal());
    this.tabArchDiagram.addEventListener("click", () => {
      this.tabArchDiagram.classList.add("active");
      this.tabInstructionsList.classList.remove("active");
      this.archDiagramView.style.display = "block";
      this.instructionsListView.style.display = "none";
    });
    this.tabInstructionsList.addEventListener("click", () => {
      this.tabInstructionsList.classList.add("active");
      this.tabArchDiagram.classList.remove("active");
      this.archDiagramView.style.display = "none";
      this.instructionsListView.style.display = "block";
      this.fetchInstructionsList();
    });

    // 7. Attendance Logs Drawer
    this.openLogsBtn.addEventListener("click", () => this.openLogsModal());
    this.viewLogsRosterBtn.addEventListener("click", () => this.openLogsModal());
    this.closeLogsModal.addEventListener("click", () => this.closeLogsModal());

    // 8. Fusion & Thresholds Modal
    this.openFusionBtn.addEventListener("click", () => this.openFusionModal());
    this.closeFusionModal.addEventListener("click", () => this.closeFusionModal());

    // Slider Listeners
    this.sliderWeightVisual.addEventListener("input", (e) => {
      this.valWeightVisual.textContent = `${e.target.value}%`;
    });
    this.sliderWeightMotion.addEventListener("input", (e) => {
      this.valWeightMotion.textContent = `${e.target.value}%`;
    });
    this.sliderWeightAudio.addEventListener("input", (e) => {
      this.valWeightAudio.textContent = `${e.target.value}%`;
    });
    this.sliderMinSustained.addEventListener("input", (e) => {
      this.valMinSustained.textContent = `${e.target.value}s`;
    });
    this.sliderSustainedRatio.addEventListener("input", (e) => {
      this.valSustainedRatio.textContent = `${e.target.value}%`;
    });
    this.sliderWalkbySeconds.addEventListener("input", (e) => {
      this.valWalkbySeconds.textContent = `${e.target.value}s`;
    });

    this.saveFusionWeightsBtn.addEventListener("click", async () => {
      const vis = parseFloat(this.sliderWeightVisual.value) / 100.0;
      const mot = parseFloat(this.sliderWeightMotion.value) / 100.0;
      const aud = parseFloat(this.sliderWeightAudio.value) / 100.0;
      const minSec = parseFloat(this.sliderMinSustained.value);
      const ratio = parseFloat(this.sliderSustainedRatio.value) / 100.0;
      const walkSec = parseFloat(this.sliderWalkbySeconds.value);

      try {
        await fetch(`/api/fusion/weights?visual=${vis}&motion=${mot}&audio=${aud}&drop_threshold=25.0`, { method: "POST" });
        await fetch(`/api/attendance/config?min_seconds=${minSec}&ratio=${ratio}&walkby_seconds=${walkSec}`, { method: "POST" });
        this.fusionModal.style.display = "none";
        alert("Parameters updated successfully! Multimodal Fusion model re-weighted.");
      } catch (e) {
        console.error("Failed to update weights:", e);
      }
    });

    // 9. Storage Layer Modal
    this.openStorageBtn.addEventListener("click", () => this.openStorageModal());
    this.closeStorageModal.addEventListener("click", () => this.closeStorageModal());
    this.tabStorageAudio.addEventListener("click", () => this.setStorageTab("audio"));
    this.tabStorageCode.addEventListener("click", () => this.setStorageTab("code"));
    this.tabStorageUploads.addEventListener("click", () => this.setStorageTab("uploads"));

    // 10. Automated Tests Modal (Instruction 15)
    this.openTestsBtn.addEventListener("click", () => this.openTestsModal());
    this.closeTestsModal.addEventListener("click", () => this.closeTestsModal());
    this.executeTestsBtn.addEventListener("click", () => this.runSystemTestsSuite());

    // 11. Visual Aid Modal (Gemini Image/Diagram Generator)
    this.quickVisualAidBtn.addEventListener("click", () => this.openVisualAidModal());
    this.triggerVisualAidModalBtn.addEventListener("click", () => this.openVisualAidModal());
    this.closeVisualAidModal.addEventListener("click", () => this.closeVisualAidModal());

    // 12. Activity 3.2 Audio Modal
    if (this.openAudioAnalysisBtn) {
      this.openAudioAnalysisBtn.addEventListener("click", () => this.openAudioAnalysisModal());
    }
    if (this.closeAudioAnalysisModal) {
      this.closeAudioAnalysisModal.addEventListener("click", () => this.closeAudioAnalysisModal());
    }

    // 9. Multimodal Agent Modal Trigger
    if (this.openMultimodalAgentBtn) {
      this.openMultimodalAgentBtn.addEventListener("click", () => this.openMultimodalAgentModal());
    }

    // 10. Activity 4.2 Multimodal Signal Fusion Modal Trigger
    if (this.openFusionActivityBtn) {
      this.openFusionActivityBtn.addEventListener("click", () => this.openFusionActivityModal());
    }

    // 11. Activity 4.3 Engagement Scoring Logic Modal Trigger
    if (this.openScoringActivityBtn) {
      this.openScoringActivityBtn.addEventListener("click", () => this.openScoringActivityModal());
    }

    // 12. Activity 5.1 Teaching Suggestion Logic Modal Trigger
    if (this.openRecommendationsBtn) {
      this.openRecommendationsBtn.addEventListener("click", () => this.openRecommendationsModal());
    }

    // 13. Activity 5.2 Student Session Analytics Modal Trigger
    if (this.openStudentAnalyticsBtn) {
      this.openStudentAnalyticsBtn.addEventListener("click", () => this.openStudentAnalyticsModal());
    }

    // Close modals on Escape key
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" || e.keyCode === 27) {
        this.closeAllModals();
      }
    });

    // Close modals on backdrop click
    window.addEventListener("click", (e) => {
      const allModals = [
        this.architectureModal, this.logsModal, this.fusionModal, this.storageModal,
        this.testsModal, this.visualAidModal, this.audioAnalysisModal,
        this.multimodalAgentModal, this.fusionActivityModal, this.scoringActivityModal,
        this.recommendationsModal, this.studentAnalyticsModal, this.coreAppModal, this.identifyModal
      ];
      allModals.forEach(m => {
        if (m && e.target === m) {
          this._hideModal(m);
        }
      });
      // Close Activity Explorer dropdown if clicked outside
      const dropdownMenu = document.getElementById("activityDropdownMenu");
      const dropdownBtn = document.getElementById("activityDropdownBtn");
      if (dropdownMenu && dropdownMenu.classList.contains("show")) {
        if (!dropdownMenu.contains(e.target) && (!dropdownBtn || !dropdownBtn.contains(e.target))) {
          dropdownMenu.classList.remove("show");
        }
      }
    });
  }

  // --- Centralized Modal Viewport & Body Scroll Management ---
  _showModal(modalEl) {
    if (!modalEl) return;
    // Dismiss Activity Explorer dropdown
    const dropdownMenu = document.getElementById("activityDropdownMenu");
    if (dropdownMenu) dropdownMenu.classList.remove("show");

    modalEl.classList.remove("hidden");
    modalEl.classList.add("active");
    modalEl.style.display = "flex";
    document.body.style.overflow = "hidden";
  }

  _hideModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.remove("active");
    modalEl.classList.add("hidden");
    modalEl.style.display = "none";

    const anyActive = document.querySelector(".modal-backdrop.active, .modal-overlay.active, .modal-backdrop[style*='display: flex'], .modal-overlay[style*='display: flex']");
    if (!anyActive) {
      document.body.style.overflow = "";
    }
  }

  closeAllModals() {
    const allModals = [
      this.architectureModal, this.logsModal, this.fusionModal, this.storageModal,
      this.testsModal, this.visualAidModal, this.audioAnalysisModal,
      this.multimodalAgentModal, this.fusionActivityModal, this.scoringActivityModal,
      this.recommendationsModal, this.studentAnalyticsModal, this.coreAppModal, this.identifyModal
    ];
    allModals.forEach(m => this._hideModal(m));
    const dropdownMenu = document.getElementById("activityDropdownMenu");
    if (dropdownMenu) dropdownMenu.classList.remove("show");
  }

  showToast(message, type = "info") {
    let toast = document.getElementById("neuroToast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "neuroToast";
      toast.style.position = "fixed";
      toast.style.bottom = "24px";
      toast.style.right = "24px";
      toast.style.padding = "12px 20px";
      toast.style.borderRadius = "8px";
      toast.style.fontSize = "13px";
      toast.style.fontWeight = "600";
      toast.style.zIndex = "9999";
      toast.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.6)";
      toast.style.transition = "all 0.3s ease";
      toast.style.display = "flex";
      toast.style.alignItems = "center";
      toast.style.gap = "10px";
      document.body.appendChild(toast);
    }
    const icon = type === "success" ? "✅" : (type === "error" ? "⚠️" : "ℹ️");
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    if (type === "success") {
      toast.style.background = "rgba(16, 185, 129, 0.95)";
      toast.style.color = "#ffffff";
      toast.style.border = "1px solid #34d399";
    } else if (type === "error") {
      toast.style.background = "rgba(239, 68, 68, 0.95)";
      toast.style.color = "#ffffff";
      toast.style.border = "1px solid #f87171";
    } else {
      toast.style.background = "rgba(15, 23, 42, 0.95)";
      toast.style.color = "#38bdf8";
      toast.style.border = "1px solid #38bdf8";
    }
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";
    clearTimeout(this._toastTimeout);
    this._toastTimeout = setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
    }, 4000);
  }

  // --- Modal Open/Close Explicit Methods ---
  openArchitectureModal() {
    this._showModal(this.architectureModal);
    this.fetchInstructionsList();
  }
  closeArchitectureModal() {
    this._hideModal(this.architectureModal);
  }

  openLogsModal() {
    this._showModal(this.logsModal);
    this.fetchDetailedAttendanceLogs();
  }
  closeLogsModal() {
    this._hideModal(this.logsModal);
  }

  openFusionModal() {
    this._showModal(this.fusionModal);
    this.fetchFusionWeights();
  }
  closeFusionModal() {
    this._hideModal(this.fusionModal);
  }

  openStorageModal() {
    this._showModal(this.storageModal);
    this.fetchStorageFiles();
  }
  closeStorageModal() {
    this._hideModal(this.storageModal);
  }

  openTestsModal() {
    this._showModal(this.testsModal);
    this.runSystemTestsSuite();
  }
  closeTestsModal() {
    this._hideModal(this.testsModal);
  }

  async openVisualAidModal() {
    try {
      const res = await fetch("/api/ai/visual_aid?topic=Multimodal+Classroom+Signal+Fusion");
      const data = await res.json();
      this.visualAidTitle.textContent = data.title;
      this.visualAidSvgContainer.innerHTML = data.svg;
      this._showModal(this.visualAidModal);
    } catch (e) {
      console.error("Failed to generate visual aid:", e);
    }
  }
  closeVisualAidModal() {
    this._hideModal(this.visualAidModal);
  }

  // --- Activity 4.1 Multimodal Agent Modal Methods ---
  openMultimodalAgentModal() {
    this._showModal(this.multimodalAgentModal);
    this.fetchMultimodalAgentStatus();
  }

  closeMultimodalAgentModal() {
    this._hideModal(this.multimodalAgentModal);
  }

  async fetchMultimodalAgentStatus() {
    try {
      const res = await fetch("/api/agent/activity_4_1/status");
      const data = await res.json();
      if (data && data.latest_reasoning_result) {
        this.updateMultimodalAgentModalState(data.latest_reasoning_result);
      }
    } catch (e) {
      console.warn("Could not fetch Activity 4.1 status:", e);
    }
  }

  updateMultimodalAgentModalState(res) {
    if (!res) return;
    if (this.agentModalEiValue && res.engagement_index !== undefined) {
      this.agentModalEiValue.textContent = `${res.engagement_index.toFixed(1)}%`;
    }
    if (this.agentModalStatePill && res.engagement_state) {
      this.agentModalStatePill.textContent = res.engagement_state;
      if (res.engagement_state === 'HIGH_FLOW' || res.engagement_state === 'COLLABORATIVE_ACTIVE') {
        this.agentModalStatePill.style.background = '#10b981';
        this.agentModalStatePill.style.color = '#022c22';
      } else if (res.engagement_state === 'PASSIVE_DISENGAGEMENT' || res.engagement_state === 'CONCEPT_HESITATION') {
        this.agentModalStatePill.style.background = '#f59e0b';
        this.agentModalStatePill.style.color = '#451a03';
      } else if (res.engagement_state === 'ACOUSTIC_DISRUPTION' || res.engagement_state === 'FATIGUE_RESTLESSNESS') {
        this.agentModalStatePill.style.background = '#ef4444';
        this.agentModalStatePill.style.color = '#450a0a';
      } else {
        this.agentModalStatePill.style.background = 'rgba(56, 189, 248, 0.2)';
        this.agentModalStatePill.style.color = '#38bdf8';
      }
    }
    if (this.agentModalTrendPill) {
      const trend = res.trend || 'STABLE';
      const delta = res.trend_delta || 0.0;
      this.agentModalTrendPill.textContent = `${trend} (${delta > 0 ? '+' : ''}${delta.toFixed(1)}%)`;
    }
    if (this.agentModalDominantModality && res.dominant_modality) {
      this.agentModalDominantModality.textContent = res.dominant_modality;
    }
    if (this.agentModalConfidenceBadge && res.confidence !== undefined) {
      this.agentModalConfidenceBadge.textContent = `${Math.round(res.confidence * 100)}% Confidence`;
    }
    if (this.agentModalRuleId && res.rule_triggered) {
      this.agentModalRuleId.textContent = res.rule_triggered;
    }
    if (this.agentModalDiagnosisText && res.explainable_diagnosis) {
      this.agentModalDiagnosisText.textContent = res.explainable_diagnosis;
    }
    if (res.factor_breakdown) {
      if (this.agentModalVisFactor && res.factor_breakdown.visual_attention_component !== undefined) {
        this.agentModalVisFactor.textContent = `${res.factor_breakdown.visual_attention_component.toFixed(1)}%`;
      }
      if (this.agentModalMotFactor && res.factor_breakdown.motion_balance_component !== undefined) {
        this.agentModalMotFactor.textContent = `${res.factor_breakdown.motion_balance_component.toFixed(1)}%`;
      }
      if (this.agentModalAudFactor && res.factor_breakdown.audio_interaction_component !== undefined) {
        this.agentModalAudFactor.textContent = `${res.factor_breakdown.audio_interaction_component.toFixed(1)}%`;
      }
    }
    if (this.agentModalLlmInsightText && res.actionable_insight) {
      this.agentModalLlmInsightText.textContent = res.actionable_insight;
    }
    if (this.agentModalLlmRecommendationText && res.teaching_recommendation) {
      this.agentModalLlmRecommendationText.textContent = res.teaching_recommendation;
    }
    if (this.agentModalModelBadge && res.raw_inputs && res.raw_inputs.llm_model) {
      this.agentModalModelBadge.textContent = res.raw_inputs.llm_model;
    }
  }

  async refreshLlmInsight() {
    try {
      if (this.agentModalLlmInsightText) this.agentModalLlmInsightText.textContent = "Synthesizing latest educational insights via Groq...";
      if (this.agentModalLlmRecommendationText) this.agentModalLlmRecommendationText.textContent = "Analyzing multimodal vectors...";
      const res = await fetch("/api/agent/activity_4_1/llm_insight", { method: "POST" });
      const data = await res.json();
      if (data && data.insight_result) {
        const r = data.insight_result;
        if (this.agentModalLlmInsightText) this.agentModalLlmInsightText.textContent = r.insight;
        if (this.agentModalLlmRecommendationText) this.agentModalLlmRecommendationText.textContent = r.recommendation;
        if (this.agentModalModelBadge) this.agentModalModelBadge.textContent = r.model;
      }
    } catch (e) {
      console.warn("Error refreshing LLM insight:", e);
    }
  }

  // --- Activity 4.2 Multimodal Signal Fusion Methods ---
  openFusionActivityModal() {
    this._showModal(this.fusionActivityModal);
    this.fetchFusionActivityStatus();
  }

  closeFusionActivityModal() {
    this._hideModal(this.fusionActivityModal);
  }

  async fetchFusionActivityStatus() {
    try {
      const res = await fetch("/api/fusion/activity_4_2/status");
      const data = await res.json();
      if (data && data.latest_unified_representation) {
        this.updateFusionActivityModalUI(data.latest_unified_representation);
      }
    } catch (e) {
      console.warn("Could not fetch Activity 4.2 status:", e);
    }
  }

  updateFusionActivityModalUI(t) {
    if (!t) return;
    if (this.fusionSyncJitter && t.sync_jitter_ms !== undefined) {
      this.fusionSyncJitter.textContent = `${t.sync_jitter_ms.toFixed(1)} ms`;
    }
    if (this.fusionCrossCorr && t.cross_modal_correlation !== undefined) {
      this.fusionCrossCorr.textContent = t.cross_modal_correlation.toFixed(2);
    }
    if (this.fusionCoherence && t.cross_modal_coherence !== undefined) {
      this.fusionCoherence.textContent = `${Math.round(t.cross_modal_coherence * 100)}%`;
    }
    if (this.fusionDominantModality && t.dominant_modality) {
      this.fusionDominantModality.textContent = t.dominant_modality;
    }
    if (this.fusionMovementPattern && t.movement_pattern) {
      this.fusionMovementPattern.textContent = t.movement_pattern;
    }
    if (this.fusionVisualAttention) {
      const vVal = t.average_visual_attention !== undefined ? t.average_visual_attention * 100 : (t.visual_attention !== undefined ? t.visual_attention : 80);
      this.fusionVisualAttention.textContent = `${vVal.toFixed(1)}%`;
    }
    if (this.fusionPresenceDuration && (t.presence_duration_seconds !== undefined || t.session_elapsed_seconds !== undefined)) {
      const pSec = t.presence_duration_seconds !== undefined ? t.presence_duration_seconds : t.session_elapsed_seconds;
      this.fusionPresenceDuration.textContent = `${Math.round(pSec)} s`;
    }
    if (this.fusionMotionEnergy) {
      const mVal = t.average_motion_energy !== undefined ? t.average_motion_energy : (t.motion_energy !== undefined ? t.motion_energy : 0.05);
      this.fusionMotionEnergy.textContent = mVal.toFixed(3);
    }
    if (this.fusionInactivitySec && t.inactivity_seconds !== undefined) {
      this.fusionInactivitySec.textContent = `${t.inactivity_seconds.toFixed(1)} s`;
    }
    if (this.fusionVisContrib && t.visual_contribution !== undefined) {
      this.fusionVisContrib.textContent = `${t.visual_contribution.toFixed(1)}%`;
    }
    if (this.fusionSpeechState && (t.speech_state || t.signal_classification)) {
      this.fusionSpeechState.textContent = t.speech_state || t.signal_classification;
    }
    if (this.fusionNoiseSpl && t.noise_level_spl !== undefined) {
      this.fusionNoiseSpl.textContent = `${t.noise_level_spl.toFixed(1)} dB SPL`;
    }
    if (this.fusionRhythmState && (t.rhythm_state || t.audio_rhythm)) {
      this.fusionRhythmState.textContent = t.rhythm_state || t.audio_rhythm;
    }
    if (this.fusionPartFreq && t.participation_frequency !== undefined) {
      this.fusionPartFreq.textContent = `${t.participation_frequency.toFixed(1)} turns/min`;
    }
    if (this.fusionSpeakerTurns && (t.speaker_turns_count !== undefined || t.speaker_turns !== undefined)) {
      this.fusionSpeakerTurns.textContent = t.speaker_turns_count !== undefined ? t.speaker_turns_count : t.speaker_turns;
    }
    if (this.fusionAudContrib && t.audio_contribution !== undefined) {
      this.fusionAudContrib.textContent = `${t.audio_contribution.toFixed(1)}%`;
    }
  }

  async triggerAiSuggestions() {
    try {
      if (this.aiSuggestionsContainer) {
        this.aiSuggestionsContainer.innerHTML = '<div style="color: #c084fc; font-size: 12px; padding: 10px;">Generating AI suggestions via Groq llama3-8b-8192...</div>';
      }
      const res = await fetch("/api/fusion/activity_4_2/generate_ai_suggestions", { method: "POST" });
      const data = await res.json();
      if (data && data.suggestions && data.suggestions.length > 0) {
        this.aiSuggestionsContainer.innerHTML = data.suggestions.map(s => `
          <div style="background: rgba(15, 23, 42, 0.4); padding: 12px; border-radius: 8px; border-left: 3px solid #c084fc; margin-bottom: 8px;">
            <strong style="color: #c084fc; font-size: 13px;">TITLE: ${s.title || "Teaching Suggestion"}</strong>
            <p style="font-size: 12px; color: #e2e8f0; margin: 4px 0 0 0;"><strong>ACTION:</strong> ${s.action || ""}</p>
            <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;"><strong>RATIONALE:</strong> ${s.rationale || ""}</p>
          </div>
        `).join("");
      }
    } catch (e) {
      console.warn("Could not generate AI suggestions:", e);
    }
  }

  async testCustomModality() {
    try {
      const mockModality = {
        modality_name: "smart_whiteboard_pen",
        data: {
          active_pen_strokes: 58,
          board_quadrant: "CENTER_TOP",
          stroke_velocity: 1.42,
          timestamp: Date.now() / 1000
        }
      };
      const res = await fetch("/api/fusion/activity_4_2/add_modality", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mockModality)
      });
      const data = await res.json();
      if (data && data.status === "SUCCESS") {
        const tag = document.createElement("span");
        tag.className = "badge-tag";
        tag.style.background = "rgba(168, 85, 247, 0.25)";
        tag.style.color = "#c084fc";
        tag.style.border = "1px solid rgba(168, 85, 247, 0.5)";
        tag.textContent = `Modality: ${data.modality_registered} (Synced)`;
        if (this.fusionCustomModalitiesList) {
          this.fusionCustomModalitiesList.appendChild(tag);
        }
      }
    } catch (e) {
      console.warn("Error injecting test modality:", e);
    }
  }

  // --- Activity 4.3 Engagement Scoring Logic Methods ---
  openScoringActivityModal() {
    this._showModal(this.scoringActivityModal);
    this.fetchScoringActivityStatus();
    this.refreshTemporalProfile();
  }

  closeScoringActivityModal() {
    this._hideModal(this.scoringActivityModal);
  }

  async fetchScoringActivityStatus() {
    try {
      const res = await fetch("/api/engagement/activity_4_3/status");
      const data = await res.json();
      if (data && data.latest_segment_score) {
        this.updateScoringActivityModalUI(data.latest_segment_score);
      }
      if (data && data.threshold_config) {
        this.updateScoringThresholdConfigUI(data.threshold_config);
      }
    } catch (e) {
      console.warn("Could not fetch Activity 4.3 status:", e);
    }
  }

  updateScoringActivityModalUI(score) {
    if (!score) return;
    if (this.scoringCompositeVal && score.composite_score !== undefined) {
      this.scoringCompositeVal.textContent = `${score.composite_score.toFixed(1)}%`;
    }
    if (this.scoringTierBadge && score.engagement_level) {
      this.scoringTierBadge.textContent = score.engagement_level;
      if (score.engagement_level === "HIGH") {
        this.scoringTierBadge.style.background = "rgba(16, 185, 129, 0.2)";
        this.scoringTierBadge.style.color = "#34d399";
      } else if (score.engagement_level === "MODERATE") {
        this.scoringTierBadge.style.background = "rgba(56, 189, 248, 0.2)";
        this.scoringTierBadge.style.color = "#38bdf8";
      } else if (score.engagement_level === "LOW") {
        this.scoringTierBadge.style.background = "rgba(245, 158, 11, 0.2)";
        this.scoringTierBadge.style.color = "#f59e0b";
      } else {
        this.scoringTierBadge.style.background = "rgba(239, 68, 68, 0.2)";
        this.scoringTierBadge.style.color = "#ef4444";
      }
    }

    if (this.scoringVisScore && score.visual_presence_score !== undefined) {
      this.scoringVisScore.textContent = `${score.visual_presence_score.toFixed(1)}%`;
    }
    if (this.scoringMotScore && score.movement_frequency_score !== undefined) {
      this.scoringMotScore.textContent = `${score.movement_frequency_score.toFixed(1)}%`;
    }
    if (this.scoringInaScore && score.inactivity_score !== undefined) {
      this.scoringInaScore.textContent = `${score.inactivity_score.toFixed(1)}%`;
    }
    if (this.scoringAudScore && score.speech_intensity_score !== undefined) {
      this.scoringAudScore.textContent = `${score.speech_intensity_score.toFixed(1)}%`;
    }

    const attr = score.factor_attribution;
    if (attr) {
      if (this.scoringVisContrib && attr.visual_presence_contribution !== undefined) {
        this.scoringVisContrib.textContent = attr.visual_presence_contribution.toFixed(1);
      }
      if (this.scoringMotContrib && attr.movement_frequency_contribution !== undefined) {
        this.scoringMotContrib.textContent = attr.movement_frequency_contribution.toFixed(1);
      }
      if (this.scoringInaContrib && attr.inactivity_contribution !== undefined) {
        this.scoringInaContrib.textContent = attr.inactivity_contribution.toFixed(1);
      }
      if (this.scoringAudContrib && attr.speech_intensity_contribution !== undefined) {
        this.scoringAudContrib.textContent = attr.speech_intensity_contribution.toFixed(1);
      }
      if (this.scoringDominantDriver && attr.dominant_driver) {
        this.scoringDominantDriver.textContent = `Dominant Driver: ${attr.dominant_driver}`;
      }
    }
  }

  updateScoringThresholdConfigUI(cfg) {
    if (!cfg) return;
    if (this.activePresetBadge && cfg.preset_name) {
      this.activePresetBadge.textContent = `Preset: ${cfg.preset_name}`;
    }
    if (this.inputWeightVis && cfg.weight_visual !== undefined) {
      this.inputWeightVis.value = cfg.weight_visual;
      if (this.valWeightVis) this.valWeightVis.textContent = cfg.weight_visual.toFixed(2);
      if (this.scoringVisWeight) this.scoringVisWeight.textContent = `${Math.round(cfg.weight_visual * 100)}%`;
    }
    if (this.inputWeightMot && cfg.weight_movement !== undefined) {
      this.inputWeightMot.value = cfg.weight_movement;
      if (this.valWeightMot) this.valWeightMot.textContent = cfg.weight_movement.toFixed(2);
      if (this.scoringMotWeight) this.scoringMotWeight.textContent = `${Math.round(cfg.weight_movement * 100)}%`;
    }
    if (this.inputWeightIna && cfg.weight_inactivity !== undefined) {
      this.inputWeightIna.value = cfg.weight_inactivity;
      if (this.valWeightIna) this.valWeightIna.textContent = cfg.weight_inactivity.toFixed(2);
      if (this.scoringInaWeight) this.scoringInaWeight.textContent = `${Math.round(cfg.weight_inactivity * 100)}%`;
    }
    if (this.inputWeightAud && cfg.weight_speech !== undefined) {
      this.inputWeightAud.value = cfg.weight_speech;
      if (this.valWeightAud) this.valWeightAud.textContent = cfg.weight_speech.toFixed(2);
      if (this.scoringAudWeight) this.scoringAudWeight.textContent = `${Math.round(cfg.weight_speech * 100)}%`;
    }
  }

  async onThresholdSliderChange() {
    const wVis = parseFloat(this.inputWeightVis ? this.inputWeightVis.value : 0.35);
    const wMot = parseFloat(this.inputWeightMot ? this.inputWeightMot.value : 0.20);
    const wIna = parseFloat(this.inputWeightIna ? this.inputWeightIna.value : 0.15);
    const wAud = parseFloat(this.inputWeightAud ? this.inputWeightAud.value : 0.30);

    try {
      const res = await fetch("/api/engagement/activity_4_3/update_thresholds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          weight_visual: wVis,
          weight_movement: wMot,
          weight_inactivity: wIna,
          weight_speech: wAud
        })
      });
      const data = await res.json();
      if (data && data.config) {
        this.updateScoringThresholdConfigUI(data.config);
        this.refreshTemporalProfile();
      }
    } catch (e) {
      console.warn("Failed to update thresholds:", e);
    }
  }

  async applyScoringPreset(presetName) {
    try {
      const res = await fetch(`/api/engagement/activity_4_3/apply_preset?preset=${encodeURIComponent(presetName)}`, {
        method: "POST"
      });
      const data = await res.json();
      if (data && data.config) {
        this.updateScoringThresholdConfigUI(data.config);
        this.refreshTemporalProfile();
      }
    } catch (e) {
      console.warn("Failed to apply scoring preset:", e);
    }
  }

  async refreshTemporalProfile() {
    try {
      const res = await fetch("/api/engagement/activity_4_3/temporal_profile");
      const data = await res.json();
      if (data && data.profile) {
        this.renderTemporalProfileUI(data.profile);
      }
    } catch (e) {
      console.warn("Could not refresh temporal profile:", e);
    }
  }

  renderTemporalProfileUI(p) {
    if (!p) return;
    if (this.scoringStabilityVal && p.fluctuation_metrics) {
      this.scoringStabilityVal.textContent = `${p.fluctuation_metrics.stability_score.toFixed(1)}%`;
      if (this.scoringFlucIndex) {
        this.scoringFlucIndex.textContent = `Fluctuation Index: ${p.fluctuation_metrics.fluctuation_index.toFixed(2)}`;
      }
    }
    if (this.scoringPeaksCount) {
      this.scoringPeaksCount.textContent = p.peak_periods ? p.peak_periods.length : 0;
    }
    if (this.scoringDisengageCount) {
      this.scoringDisengageCount.textContent = p.disengagement_phases ? p.disengagement_phases.length : 0;
    }

    // Render Timeline Bar Chart
    if (this.temporalProfileChartContainer && p.segments && p.segments.length > 0) {
      this.temporalProfileChartContainer.innerHTML = "";
      p.segments.forEach((seg, i) => {
        const barWrap = document.createElement("div");
        barWrap.style.display = "flex";
        barWrap.style.flexDirection = "column";
        barWrap.style.alignItems = "center";
        barWrap.style.flex = "1";
        barWrap.style.minWidth = "22px";
        barWrap.style.height = "100%";
        barWrap.style.justifyContent = "flex-end";
        barWrap.title = `Segment #${seg.segment_id}: ${seg.composite_score.toFixed(1)}% (${seg.engagement_level})\nDriver: ${seg.factor_attribution.dominant_driver}`;

        const bar = document.createElement("div");
        const hPct = Math.max(8, Math.min(100, seg.composite_score));
        bar.style.height = `${hPct}%`;
        bar.style.width = "100%";
        bar.style.borderRadius = "4px 4px 0 0";
        bar.style.transition = "all 0.3s ease";

        if (seg.composite_score >= 80.0) {
          bar.style.background = "linear-gradient(to top, #059669, #10b981)";
          bar.style.boxShadow = "0 0 8px rgba(16, 185, 129, 0.4)";
        } else if (seg.composite_score >= 55.0) {
          bar.style.background = "linear-gradient(to top, #0284c7, #38bdf8)";
        } else if (seg.composite_score >= 40.0) {
          bar.style.background = "linear-gradient(to top, #d97706, #f59e0b)";
        } else {
          bar.style.background = "linear-gradient(to top, #dc2626, #ef4444)";
          bar.style.boxShadow = "0 0 8px rgba(239, 68, 68, 0.4)";
        }

        const lbl = document.createElement("span");
        lbl.style.fontSize = "9px";
        lbl.style.color = "#64748b";
        lbl.style.marginTop = "4px";
        lbl.textContent = `#${seg.segment_id}`;

        barWrap.appendChild(bar);
        barWrap.appendChild(lbl);
        this.temporalProfileChartContainer.appendChild(barWrap);
      });
    }

    // Render Peaks List
    if (this.scoringPeaksList) {
      this.scoringPeaksList.innerHTML = "";
      if (p.peak_periods && p.peak_periods.length > 0) {
        p.peak_periods.forEach(pk => {
          const item = document.createElement("div");
          item.style.background = "rgba(15, 23, 42, 0.4)";
          item.style.padding = "8px";
          item.style.borderRadius = "6px";
          item.innerHTML = `
            <span style="color: #34d399; font-weight: 600;">Peak #${pk.peak_id}: ${pk.average_score.toFixed(1)}% Avg (Peak: ${pk.peak_score.toFixed(1)}%)</span>
            <p style="color: #94a3b8; margin: 2px 0 0 0;">Duration: ${pk.duration_seconds.toFixed(0)}s (Segments ${pk.start_segment}-${pk.end_segment}) • Drivers: ${pk.dominant_drivers.join(", ")}</p>
          `;
          this.scoringPeaksList.appendChild(item);
        });
      } else {
        this.scoringPeaksList.innerHTML = `<div style="color: #64748b; font-size: 11px;">No peak engagement periods recorded yet in this session.</div>`;
      }
    }

    // Render Disengagements List
    if (this.scoringDisengagementsList) {
      this.scoringDisengagementsList.innerHTML = "";
      if (p.disengagement_phases && p.disengagement_phases.length > 0) {
        p.disengagement_phases.forEach(ph => {
          const item = document.createElement("div");
          item.style.background = "rgba(15, 23, 42, 0.4)";
          item.style.padding = "8px";
          item.style.borderRadius = "6px";
          item.innerHTML = `
            <span style="color: #f87171; font-weight: 600;">Phase #${ph.phase_id} (${ph.severity}): ${ph.average_score.toFixed(1)}% Avg</span>
            <p style="color: #e2e8f0; margin: 2px 0 0 0;">Cause: ${ph.primary_cause} • Duration: ${ph.duration_seconds.toFixed(0)}s</p>
            <p style="color: #38bdf8; margin: 2px 0 0 0; font-size: 10px;">Action: ${ph.suggested_action}</p>
          `;
          this.scoringDisengagementsList.appendChild(item);
        });
      } else {
        this.scoringDisengagementsList.innerHTML = `<div style="color: #10b981; font-size: 11px;">✓ No extended disengagement phases detected. Engagement is stable.</div>`;
      }
    }
  }

  async triggerDownstreamSummary() {
    try {
      const res = await fetch("/api/engagement/activity_4_3/downstream_summary", { method: "POST" });
      const data = await res.json();
      if (data && data.teaching_suggestions) {
        alert(`Downstream Intelligence Generated!\n\nTeaching Suggestions: ${data.teaching_suggestions.length} cards\nStudent Analytics: ${data.student_analytics.total_students} profiles\nSession Status: ${data.session_summary.pedagogical_takeaway || 'Ready'}`);
      }
    } catch (e) {
      console.warn("Error triggering downstream summary:", e);
    }
  }

  // --- Activity 5.1 Teaching Suggestion Logic Methods ---
  openRecommendationsModal() {
    this._showModal(this.recommendationsModal);
    this.fetchRecommendationsStatus();
  }

  closeRecommendationsModal() {
    this._hideModal(this.recommendationsModal);
  }

  async fetchRecommendationsStatus() {
    try {
      const res = await fetch("/api/recommendations/activity_5_1/status");
      const data = await res.json();
      if (data && data.teacher_profile) {
        this.updateTeacherProfileUI(data.teacher_profile);
      }
      if (data && data.recent_recommendations) {
        this.updateRecommendationsUI(data.recent_recommendations);
      }
    } catch (e) {
      console.warn("Could not fetch Activity 5.1 status:", e);
    }
  }

  updateTeacherProfileUI(p) {
    if (!p) return;
    if (this.recTeacherName) this.recTeacherName.textContent = p.teacher_id || "Prof. Alex Vance";
    if (this.recEffectivenessScore && p.effectiveness_score !== undefined) {
      this.recEffectivenessScore.textContent = `${p.effectiveness_score.toFixed(1)}%`;
    }
    if (this.recEffectivenessTrend && p.trend !== undefined) {
      const tr = p.trend;
      this.recEffectivenessTrend.textContent = `${tr > 0 ? '+' : ''}${tr.toFixed(1)}% ↗`;
    }
    if (this.recClassHistoryList && p.class_history) {
      this.recClassHistoryList.innerHTML = p.class_history.map(c => `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #cbd5e1;">${c.name}</span>
          <span style="color: ${c.engagement >= 85 ? '#34d399' : '#38bdf8'}; font-weight: 700;">${c.engagement}%</span>
        </div>
      `).join("");
    }
    if (this.recStudentTrendsList && p.student_trends) {
      this.recStudentTrendsList.innerHTML = p.student_trends.map(s => `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="color: #cbd5e1;">${s.name}</span>
          <span style="color: ${s.status === 'improved' ? '#34d399' : s.status === 'declining' ? '#f87171' : '#94a3b8'}; font-weight: 600;">
            ${s.change > 0 ? '+' : ''}${s.change}% (${s.status})
          </span>
        </div>
      `).join("");
    }
    if (this.recStrengthsList && p.strengths) {
      const colors = ["#38bdf8", "#c084fc", "#4ade80", "#fbbf24"];
      this.recStrengthsList.innerHTML = p.strengths.map((str, idx) => `
        <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: ${colors[idx % colors.length]}; font-size: 10px; padding: 2px 8px; border-radius: 10px;">${str}</span>
      `).join("");
    }
  }

  updateRecommendationsUI(recs) {
    if (!this.recommendationsFeedList) return;
    if (this.recCountBadge) {
      this.recCountBadge.textContent = `${recs ? recs.length : 0} Active`;
    }
    if (!recs || recs.length === 0) {
      this.recommendationsFeedList.innerHTML = `
        <div style="color: #10b981; font-size: 12px; padding: 12px; text-align: center; background: rgba(16, 185, 129, 0.08); border-radius: 6px;">
          ✓ Classroom dynamics are balanced and healthy. No urgent intervention required.
        </div>
      `;
      return;
    }

    this.recommendationsFeedList.innerHTML = recs.map(r => {
      const isAlert = r.type === 'alert';
      const isWarning = r.type === 'warning';
      const borderCol = isAlert ? '#ef4444' : isWarning ? '#f59e0b' : '#10b981';
      const bgCol = isAlert ? 'rgba(239, 68, 68, 0.08)' : isWarning ? 'rgba(245, 158, 11, 0.08)' : 'rgba(16, 185, 129, 0.08)';
      const badgeCol = isAlert ? '#ef4444' : isWarning ? '#f59e0b' : '#10b981';
      const actionCol = isAlert ? '#93c5fd' : isWarning ? '#fde68a' : '#86efac';

      return `
        <div class="panel glass-panel" style="padding: 12px; border-left: 4px solid ${borderCol}; background: ${bgCol};">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge" style="background: rgba(255,255,255,0.1); color: ${badgeCol}; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 700;">
                ${(r.type || 'INFO').toUpperCase()}
              </span>
              <strong style="color: #f1f5f9; font-size: 12px;">${r.title || 'Pedagogical Recommendation'}</strong>
            </div>
            <span style="font-size: 10px; color: #94a3b8;">Confidence: ${Math.round((r.confidence || 0.85) * 100)}%</span>
          </div>
          <p style="margin: 4px 0; font-size: 11px; color: #cbd5e1;">${r.message}</p>
          <div style="margin-top: 6px; background: rgba(15, 23, 42, 0.4); padding: 6px 10px; border-radius: 4px; font-size: 11px; color: ${actionCol};">
            <strong>Suggested Action:</strong> ${r.pedagogical_action || 'Review pacing and engagement.'}
          </div>
        </div>
      `;
    }).join("");
  }

  async evaluateLiveRecommendations() {
    try {
      const res = await fetch("/api/recommendations/activity_5_1/generate", { method: "POST" });
      const data = await res.json();
      if (data && data.recommendations) {
        this.updateRecommendationsUI(data.recommendations);
      }
    } catch (e) {
      console.warn("Failed to evaluate recommendations:", e);
    }
  }

  async resetRecommendationCooldowns() {
    try {
      await fetch("/api/recommendations/activity_5_1/reset", { method: "POST" });
      this.fetchRecommendationsStatus();
    } catch (e) {
      console.warn("Failed to reset recommendations:", e);
    }
  }

  async simulateScenario(type) {
    let payload = {};
    if (type === 'normal') {
      payload = {
        people: [
          { id: "STU-101", name: "Emma Watson", attention: 88.0 },
          { id: "STU-102", name: "Liam Smith", attention: 82.0 },
          { id: "STU-103", name: "Sophia Chen", attention: 79.0 }
        ],
        engagement_score: 82.0,
        noise_level_spl: 52.0,
        ambient_noise_level: "MODERATE",
        consecutive_monologue_sec: 120.0,
        trend: "STABLE"
      };
    } else if (type === 'distraction') {
      payload = {
        people: [
          { id: "STU-102", name: "Liam Smith", attention: 28.5 },
          { id: "STU-101", name: "Emma Watson", attention: 75.0 },
          { id: "STU-103", name: "Sophia Chen", attention: 78.0 }
        ],
        engagement_score: 68.0,
        noise_level_spl: 54.0,
        ambient_noise_level: "MODERATE",
        consecutive_monologue_sec: 200.0,
        trend: "STABLE"
      };
    } else if (type === 'disengagement') {
      payload = {
        people: [
          { id: "STU-101", name: "Emma Watson", attention: 42.0 },
          { id: "STU-102", name: "Liam Smith", attention: 35.0 },
          { id: "STU-103", name: "Sophia Chen", attention: 44.0 }
        ],
        engagement_score: 42.0,
        inactivity_seconds: 65.0,
        noise_level_spl: 48.0,
        ambient_noise_level: "QUIET",
        consecutive_monologue_sec: 350.0,
        trend: "DROPPING",
        trend_delta: 22.0,
        disengagement_phases: [{ phase_id: 1, primary_cause: "Prolonged Inactivity", average_score: 41.5, duration_seconds: 40.0 }]
      };
    } else if (type === 'noise') {
      payload = {
        people: [
          { id: "STU-101", name: "Emma Watson", attention: 62.0 },
          { id: "STU-102", name: "Liam Smith", attention: 58.0 }
        ],
        engagement_score: 58.0,
        noise_level_spl: 78.5,
        ambient_noise_level: "LOUD_DISRUPTIVE",
        consecutive_monologue_sec: 180.0,
        trend: "STABLE"
      };
    } else if (type === 'peak') {
      payload = {
        people: [
          { id: "STU-101", name: "Emma Watson", attention: 92.0 },
          { id: "STU-102", name: "Liam Smith", attention: 89.0 },
          { id: "STU-103", name: "Sophia Chen", attention: 94.0 }
        ],
        engagement_score: 89.5,
        noise_level_spl: 62.0,
        ambient_noise_level: "MODERATE",
        consecutive_monologue_sec: 60.0,
        trend: "RISING",
        peak_periods: [{ period_id: 1, top_factor: "Dynamic Q&A & Visual Focus", average_score: 89.5, duration_seconds: 30.0 }]
      };
    }

    try {
      const res = await fetch("/api/recommendations/activity_5_1/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data && data.recommendations) {
        this.updateRecommendationsUI(data.recommendations);
      }
    } catch (e) {
      console.warn("Failed to simulate scenario:", e);
    }
  }


  // --- Activity 5.2 Student Session Analytics Methods ---
  openStudentAnalyticsModal() {
    this._showModal(this.studentAnalyticsModal);
    const selectedStudent = this.studentSelectActivity52 ? this.studentSelectActivity52.value : "STU-101";
    this.fetchStudentAnalytics(selectedStudent);
    this.fetchCohortReflective();
  }

  closeStudentAnalyticsModal() {
    this._hideModal(this.studentAnalyticsModal);
  }

  onStudentSelectedActivity52(studentId) {
    this.fetchStudentAnalytics(studentId);
  }

  refreshStudentAnalytics() {
    const selectedStudent = this.studentSelectActivity52 ? this.studentSelectActivity52.value : "STU-101";
    this.fetchStudentAnalytics(selectedStudent);
    this.fetchCohortReflective();
  }

  async fetchStudentAnalytics(studentId) {
    try {
      const res = await fetch(`/api/analytics/activity_5_2/student/${studentId}`);
      const data = await res.json();
      if (data) {
        this.updateStudentAnalyticsUI(data);
      }
    } catch (e) {
      console.warn("Could not fetch student analytics:", e);
    }
  }

  updateStudentAnalyticsUI(data) {
    if (!data) return;

    // 1. Attendance
    if (data.attendance) {
      if (this.stuAttStatusBadge) this.stuAttStatusBadge.textContent = data.attendance.status || "PRESENT";
      if (this.stuActiveDuration) this.stuActiveDuration.textContent = data.attendance.duration_formatted || "28m 45s";
      if (this.stuPresenceRatio) this.stuPresenceRatio.textContent = `(${data.attendance.presence_ratio_percent}% attended)`;
      if (this.stuFirstSeen) this.stuFirstSeen.textContent = data.attendance.first_detected || "N/A";
      if (this.stuAuditProof) this.stuAuditProof.textContent = data.attendance.verification_hash || "VERIFIED-EDGE";
    }

    // 2. Consistency
    if (data.consistency) {
      if (this.stuConsistencyBadge) this.stuConsistencyBadge.textContent = data.consistency.consistency_classification || "HIGHLY_STEADY";
      if (this.stuConsistencyScore) this.stuConsistencyScore.textContent = `${data.consistency.consistency_score}%`;
      if (this.stuConsistencyDesc) this.stuConsistencyDesc.textContent = data.consistency.stability_description || "";
    }

    // 3. Focus Distribution
    if (data.focus_distribution) {
      const fd = data.focus_distribution;
      if (this.stuBarHighFocus) this.stuBarHighFocus.style.width = `${Math.max(fd.high_focus_percent, 5)}%`;
      if (this.stuBarBalanced) this.stuBarBalanced.style.width = `${Math.max(fd.balanced_attention_percent, 5)}%`;
      if (this.stuBarDistraction) this.stuBarDistraction.style.width = `${Math.max(fd.distraction_wandering_percent, 5)}%`;

      if (this.stuHighFocusPct) this.stuHighFocusPct.textContent = `${fd.high_focus_percent}% (${fd.high_focus_episodes} eps)`;
      if (this.stuBalancedPct) this.stuBalancedPct.textContent = `${fd.balanced_attention_percent}%`;
      if (this.stuDistractPct) this.stuDistractPct.textContent = `${fd.distraction_wandering_percent}% (${fd.distraction_episodes} eps)`;
    }

    // 4. Focus Periods Timeline List
    if (this.stuFocusPeriodsList && data.focus_periods) {
      this.stuFocusPeriodsList.innerHTML = data.focus_periods.map(p => {
        const isHigh = p.zone_type === "HIGH_FOCUS";
        const isDistract = p.zone_type === "DISTRACTION_WANDERING";
        const borderCol = isHigh ? "#10b981" : (isDistract ? "#f59e0b" : "#3b82f6");
        const bgCol = isHigh ? "rgba(16, 185, 129, 0.08)" : (isDistract ? "rgba(245, 158, 11, 0.08)" : "rgba(59, 130, 246, 0.08)");
        const tagCol = isHigh ? "#34d399" : (isDistract ? "#fbbf24" : "#60a5fa");

        return `
          <div class="panel glass-panel" style="padding: 10px; border-left: 3px solid ${borderCol}; background: ${bgCol};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span class="badge" style="background: rgba(255,255,255,0.06); color: ${tagCol}; font-size: 10px; padding: 1px 6px; border-radius: 4px; font-weight: 700;">
                  ${p.zone_type}
                </span>
                <span style="color: #f1f5f9; font-size: 11px; font-weight: 600;">${p.start_time_str} - ${p.end_time_str}</span>
                <span style="color: #94a3b8; font-size: 10px;">(${p.duration_seconds.toFixed(0)}s)</span>
              </div>
              <span style="color: ${tagCol}; font-weight: 700; font-size: 11px;">${p.average_attention}% avg</span>
            </div>
            <p style="margin: 4px 0 0 0; font-size: 11px; color: #cbd5e1;">${p.notable_behavior}</p>
          </div>
        `;
      }).join("");
    }

    // 5. Notable Trends
    if (this.stuNotableTrendsList && data.notable_trends) {
      this.stuNotableTrendsList.innerHTML = data.notable_trends.map(t => `
        <div style="background: rgba(15, 23, 42, 0.4); padding: 8px 10px; border-radius: 6px; border-left: 2px solid #38bdf8;">
          <span style="color: #cbd5e1;">💡 ${t}</span>
        </div>
      `).join("");
    }

    // 6. Reflective Insights & Accountability Prompts
    if (data.reflective_insights) {
      const r = data.reflective_insights;
      if (this.stuPrimaryTakeaway) this.stuPrimaryTakeaway.textContent = r.primary_takeaway || "";
      if (this.stuQuestionsList && r.reflection_questions) {
        this.stuQuestionsList.innerHTML = r.reflection_questions.map((q, idx) => `
          <div style="background: rgba(15, 23, 42, 0.4); padding: 8px 10px; border-radius: 6px;">
            <strong style="color: #a78bfa; font-size: 10px; display: block; margin-bottom: 2px;">Question ${idx + 1}:</strong>
            <span style="color: #cbd5e1; font-style: italic;">"${q}"</span>
          </div>
        `).join("");
      }
    }
  }

  async fetchCohortReflective() {
    try {
      const res = await fetch("/api/analytics/activity_5_2/all_reflective");
      const data = await res.json();
      if (data && data.summaries && this.stuCohortTableBody) {
        this.stuCohortTableBody.innerHTML = data.summaries.map(s => `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;" onclick="window.neuroApp && window.neuroApp.onSelectCohortStudent('${s.student_id}')">
            <td style="padding: 6px 8px; font-weight: 600; color: #f8fafc;">${s.display_name}</td>
            <td style="padding: 6px 8px; color: #94a3b8;">${s.seat_label}</td>
            <td style="padding: 6px 8px; color: #38bdf8;">${s.attendance_duration}</td>
            <td style="padding: 6px 8px;">
              <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 9px; padding: 2px 6px; border-radius: 4px;">
                ${s.consistency_score}% (${s.consistency_classification})
              </span>
            </td>
            <td style="padding: 6px 8px; color: #34d399; font-weight: 700;">${s.high_focus_percent}%</td>
            <td style="padding: 6px 8px; color: #cbd5e1; font-size: 10px;">${s.notable_trend}</td>
            <td style="padding: 6px 8px;">
              <button class="btn btn-ghost" style="padding: 2px 8px; font-size: 10px;" onclick="window.neuroApp && window.neuroApp.onSelectCohortStudent('${s.student_id}')">
                Inspect 👁️
              </button>
            </td>
          </tr>
        `).join("");
      }
    } catch (e) {
      console.warn("Could not fetch cohort reflective summary:", e);
    }
  }

  onSelectCohortStudent(studentId) {
    if (this.studentSelectActivity52) {
      this.studentSelectActivity52.value = studentId;
    }
    this.fetchStudentAnalytics(studentId);
  }

  exportStudentReport(format) {
    const studentId = this.studentSelectActivity52 ? this.studentSelectActivity52.value : "STU-101";
    const url = `/api/analytics/activity_5_2/export_report/${studentId}?format_type=${format}`;
    window.open(url, "_blank");
  }


  // --- Activity 3.2 Modal Methods ---
  openAudioAnalysisModal() {
    this._showModal(this.audioAnalysisModal);
    this.fetchAudioAnalysisStatus();
  }

  closeAudioAnalysisModal() {
    this._hideModal(this.audioAnalysisModal);
  }

  toggleLiveMicFromModal() {
    if (this.isLiveMicActive) {
      this.stopLiveMicrophone();
      this.audioSourceSelect.value = "simulated";
      this.audioModeTag.textContent = "Audio: Simulated";
      if (this.modalToggleMicBtn) this.modalToggleMicBtn.textContent = "🎤 Start Live Web Microphone";
    } else {
      this.startLiveMicrophone();
      this.audioSourceSelect.value = "live_mic";
      if (this.modalToggleMicBtn) this.modalToggleMicBtn.textContent = "⏹️ Stop Live Web Microphone";
    }
  }

  async fetchAudioAnalysisStatus() {
    try {
      const res = await fetch("/api/audio/activity_3_2/status");
      const data = await res.json();
      if (data && data.current_state) {
        this.updateAudioModalState(data.current_state, data.noise_trend, data.session_context);
      }
    } catch (e) {
      console.warn("Could not fetch Activity 3.2 status:", e);
    }
  }

  updateAudioModalState(state, trend, ctx) {
    if (!state) return;
    const spl = state.noise_level_spl !== undefined ? state.noise_level_spl : 55.0;
    const dbfs = state.noise_level_db !== undefined ? state.noise_level_db : -30.0;
    const ambient = state.ambient_noise_level || "MODERATE";
    const speechState = state.speech_state || (state.vad_active ? "ACTIVE_SPEECH" : "SILENCE");

    if (this.audioModalSpl) this.audioModalSpl.textContent = `${spl.toFixed(1)} dB SPL`;
    if (this.audioModalSplBar) {
      const pct = Math.min(100, Math.max(5, ((spl - 30) / 60) * 100));
      this.audioModalSplBar.style.width = `${pct}%`;
    }
    if (this.audioModalDbfs) this.audioModalDbfs.textContent = `Digital: ${dbfs.toFixed(1)} dBFS`;
    if (this.audioModalAmbientLevel) this.audioModalAmbientLevel.textContent = ambient;

    if (this.audioModalTrend && trend) {
      const d = trend.delta_db || 0.0;
      this.audioModalTrend.textContent = `${trend.trend || 'STABLE'} (${d > 0 ? '+' : ''}${d.toFixed(1)} dB)`;
    }
    if (this.audioModalNoiseFloor && trend) {
      this.audioModalNoiseFloor.textContent = `Adaptive Floor: ${(trend.noise_floor_spl || 38.0).toFixed(1)} dB SPL`;
    }

    if (this.audioModalQuality && ctx) {
      this.audioModalQuality.textContent = `Condition: ${(ctx.environmental_acoustic_quality || 'OPTIMAL_LEARNING').replace('_', ' ')}`;
    }

    if (this.audioModalSignalStateBadge) {
      this.audioModalSignalStateBadge.textContent = speechState;
      if (speechState === 'ACTIVE_SPEECH') {
        this.audioModalSignalStateBadge.className = 'badge-present';
      } else if (speechState === 'BACKGROUND_NOISE') {
        this.audioModalSignalStateBadge.className = 'pill-chip';
      } else {
        this.audioModalSignalStateBadge.className = 'subtext';
      }
    }

    if (this.audioModalRhythm) {
      const r = state.sound_activity_pattern || state.rhythm_state || 'INSTRUCTOR_MONOLOGUE';
      this.audioModalRhythm.textContent = r.replace(/_/g, ' ');
    }
    if (this.audioModalVad) {
      this.audioModalVad.textContent = state.vad_active ? "Active Speech Detected" : "Silence / Ambient";
      this.audioModalVad.style.color = state.vad_active ? "#34d399" : "#94a3b8";
    }

    if (this.audioModalZcr && state.zero_crossing_rate !== undefined) {
      this.audioModalZcr.textContent = state.zero_crossing_rate.toFixed(4);
    }
    if (this.audioModalSpectralCentroid && state.spectral_centroid !== undefined) {
      this.audioModalSpectralCentroid.textContent = `${Math.round(state.spectral_centroid)} Hz`;
    }
    if (this.audioModalSpectralFlatness && state.spectral_flatness !== undefined) {
      this.audioModalSpectralFlatness.textContent = state.spectral_flatness.toFixed(3);
    }
    if (this.audioModalDynamicRange && state.dynamic_range_db !== undefined) {
      this.audioModalDynamicRange.textContent = `${state.dynamic_range_db.toFixed(1)} dB`;
    }

    if (this.audioModalSpeechRatio && state.speech_ratio !== undefined) {
      this.audioModalSpeechRatio.textContent = `${Math.round(state.speech_ratio * 100)}%`;
    }
    if (this.audioModalInteractionIntensity && state.interaction_intensity !== undefined) {
      this.audioModalInteractionIntensity.textContent = `${Math.round(state.interaction_intensity * 100)}%`;
    }
    if (this.audioModalParticipationFrequency && state.participation_frequency !== undefined) {
      this.audioModalParticipationFrequency.textContent = `${state.participation_frequency.toFixed(1)} / min`;
    }
    if (this.audioModalSpeakerTurns && state.speaker_turns !== undefined) {
      this.audioModalSpeakerTurns.textContent = state.speaker_turns;
    }

    if (ctx) {
      if (this.audioModalSpeechPct && ctx.speech_activity_ratio_percent !== undefined) {
        this.audioModalSpeechPct.textContent = `Speech: ${ctx.speech_activity_ratio_percent}%`;
      }
      if (this.audioModalSilencePct && ctx.silence_ratio_percent !== undefined) {
        this.audioModalSilencePct.textContent = `Silence: ${ctx.silence_ratio_percent}%`;
      }
      if (this.audioModalNoisePct && ctx.background_noise_ratio_percent !== undefined) {
        this.audioModalNoisePct.textContent = `Noise: ${ctx.background_noise_ratio_percent}%`;
      }
      if (this.audioModalMeanPeak && ctx.mean_noise_level_spl !== undefined) {
        this.audioModalMeanPeak.textContent = `Mean: ${ctx.mean_noise_level_spl} dB SPL • Peak: ${ctx.peak_noise_level_spl || ctx.mean_noise_level_spl} dB SPL`;
      }
    }
  }

  // --- Live Microphone Web Audio API Integration (Instruction 4 & Activity 3.2) ---
  async startLiveMicrophone() {
    try {
      this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioCtx({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.micStream);

      // Connect to WebSocket /ws/audio (Activity 3.2 Bidirectional Ingestion)
      const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host || 'localhost:8000';
      const wsUrl = `${wsProto}//${wsHost}/ws/audio`;

      try {
        this.micWs = new WebSocket(wsUrl);
        this.micWs.onopen = () => {
          console.log('[Microphone] WebSocket connected to /ws/audio');
          this.micWs.send(JSON.stringify({ type: 'client_handshake', source: 'app_mic' }));
        };
        this.micWs.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.metrics) {
              this.updateAudioModalState(data.metrics, data.session_context ? {
                trend: data.session_context.ambient_noise_trend,
                delta_db: data.session_context.ambient_noise_delta_db,
                noise_floor_spl: data.session_context.noise_floor_spl
              } : null, data.session_context);
            }
          } catch (err) {}
        };
      } catch (wsErr) {
        console.warn('[Microphone] WebSocket connection failed, using HTTP fallback:', wsErr);
      }

      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 512;
      source.connect(this.analyser);

      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      this.isLiveMicActive = true;

      // Send volume updates to server every 200ms
      this.micInterval = setInterval(async () => {
        if (!this.isLiveMicActive) return;
        this.analyser.getByteTimeDomainData(dataArray);
        let sumSquares = 0.0;
        const preview = [];
        for (let i = 0; i < bufferLength; i++) {
          const norm = (dataArray[i] - 128) / 128.0;
          sumSquares += norm * norm;
          if (i < 64) preview.push(norm);
        }
        const rms = Math.sqrt(sumSquares / bufferLength);
        const vad = rms > 0.025;

        // Send via WebSocket if open, else fallback to POST
        if (this.micWs && this.micWs.readyState === WebSocket.OPEN) {
          try {
            this.micWs.send(JSON.stringify({
              type: 'audio_chunk',
              rms: rms,
              vad: vad,
              samples_preview: preview,
              timestamp: Date.now() / 1000
            }));
          } catch (e) {}
        } else {
          try {
            await fetch("/api/audio/live_input", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ rms: rms, vad: vad })
            });
          } catch (err) {}
        }
      }, 200);

      this.audioModeTag.textContent = "Audio: Live Mic (Listening)";
      if (this.modalToggleMicBtn) this.modalToggleMicBtn.textContent = "⏹️ Stop Live Web Microphone";
    } catch (e) {
      console.warn("Could not access microphone, reverting to simulation:", e);
      this.audioSourceSelect.value = "simulated";
    }
  }

  stopLiveMicrophone() {
    this.isLiveMicActive = false;
    if (this.micInterval) clearInterval(this.micInterval);
    if (this.micWs) {
      try {
        this.micWs.send(JSON.stringify({ type: 'client_disconnect' }));
        this.micWs.close();
      } catch (e) {}
      this.micWs = null;
    }
    if (this.micStream) {
      this.micStream.getTracks().forEach(t => t.stop());
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
    if (this.modalToggleMicBtn) this.modalToggleMicBtn.textContent = "🎤 Start Live Web Microphone";
  }

  // --- Text-To-Speech Synthesizer & Audio Player ---
  async synthesizeAndPlayTts(text) {
    try {
      const res = await fetch(`/api/ai/tts?text=${encodeURIComponent(text)}`, { method: "POST" });
      const data = await res.json();
      if (data.url) {
        const audio = new Audio(data.url);
        audio.play().catch(() => {});
      }
    } catch (e) {
      console.error("TTS playback error:", e);
    }
  }

  // --- 15 Instructions Data Fetcher & Renderer ---
  async loadInitialInstructions() {
    try {
      const res = await fetch("/api/instructions");
      const data = await res.json();
      this.instructionsData = data.instructions || [];
    } catch (e) {}
  }

  async fetchInstructionsList() {
    try {
      const res = await fetch("/api/instructions");
      const data = await res.json();
      const list = data.instructions || [];
      this.instructionsTableBody.innerHTML = "";

      list.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${item.id}</strong></td>
          <td>
            <strong>${item.title}</strong>
            <div class="node-desc">${item.details}</div>
          </td>
          <td>
            <span class="arch-chip">${item.domain}</span>
            <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">${item.component}</div>
          </td>
          <td><span class="badge-verified">✓ ${item.status}</span></td>
          <td><span style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: var(--accent-cyan);">${item.metric}</span></td>
        `;
        this.instructionsTableBody.appendChild(tr);
      });
    } catch (e) {
      console.error("Failed to load instructions:", e);
    }
  }

  // --- Detailed Attendance Logs Fetcher & Renderer (Instruction 7) ---
  async fetchDetailedAttendanceLogs() {
    try {
      const res = await fetch("/api/attendance/logs");
      const data = await res.json();
      const records = data.records || [];
      this.logsTotalCount.textContent = `Total Enrolled Records: ${records.length} | Session: ${data.session_id}`;
      this.attendanceLogsTableBody.innerHTML = "";

      records.forEach(r => {
        const tr = document.createElement("tr");
        const mins = Math.floor(r.total_active_seconds / 60);
        const secs = Math.floor(r.total_active_seconds % 60);
        const statusClass = `status-${r.status.toLowerCase()}`;

        const isUnlinked = r.student_id && r.student_id.startsWith("TRK-");
        const linkBtn = isUnlinked ? `
          <button class="btn btn-sm btn-link-track" onclick="window.neuroApp &amp;&amp; window.neuroApp.openIdentifyModal('${r.student_id}')" title="Link or enroll this live learner" style="margin-left: 6px; font-size: 10px; padding: 2px 7px; background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #38bdf8; border-radius: 4px; cursor: pointer; font-weight: 700;">
            🎯 Identify / Link
          </button>
        ` : '';

        tr.innerHTML = `
          <td><strong>${r.student_id}</strong></td>
          <td>${r.display_name} ${linkBtn}</td>
          <td>${r.first_seen}</td>
          <td>${r.last_seen}</td>
          <td>${mins}m ${secs}s</td>
          <td>${r.presence_percentage}%</td>
          <td><span class="status-badge ${statusClass}">${r.status}</span></td>
          <td><span class="hash-cell" title="${r.verification_hash}">${r.verification_hash.substring(0, 16)}...</span></td>
        `;
        this.attendanceLogsTableBody.appendChild(tr);
      });
    } catch (e) {
      console.error("Failed to load attendance logs:", e);
    }
  }

  // --- Multimodal Fusion Weights Fetcher ---
  async fetchFusionWeights() {
    try {
      const res = await fetch("/api/fusion/weights");
      const data = await res.json();
      this.sliderWeightVisual.value = Math.round((data.weight_visual || 0.5) * 100);
      this.sliderWeightMotion.value = Math.round((data.weight_motion || 0.2) * 100);
      this.sliderWeightAudio.value = Math.round((data.weight_audio || 0.3) * 100);
      this.valWeightVisual.textContent = `${this.sliderWeightVisual.value}%`;
      this.valWeightMotion.textContent = `${this.sliderWeightMotion.value}%`;
      this.valWeightAudio.textContent = `${this.sliderWeightAudio.value}%`;

      const cfgRes = await fetch("/api/attendance/config");
      const cfgData = await cfgRes.json();
      this.sliderMinSustained.value = cfgData.min_sustained_seconds || 30;
      this.sliderSustainedRatio.value = Math.round((cfgData.sustained_ratio || 0.65) * 100);
      this.sliderWalkbySeconds.value = cfgData.walkby_threshold_seconds || 15;
      this.valMinSustained.textContent = `${this.sliderMinSustained.value}s`;
      this.valSustainedRatio.textContent = `${this.sliderSustainedRatio.value}%`;
      this.valWalkbySeconds.textContent = `${this.sliderWalkbySeconds.value}s`;
    } catch (e) {
      console.error("Failed to load fusion weights:", e);
    }
  }

  // --- Storage Files Fetcher ---
  setStorageTab(tab) {
    [this.tabStorageAudio, this.tabStorageCode, this.tabStorageUploads].forEach(b => b.classList.remove("active"));
    [this.storageAudioView, this.storageCodeView, this.storageUploadsView].forEach(v => v.style.display = "none");

    if (tab === "audio") {
      this.tabStorageAudio.classList.add("active");
      this.storageAudioView.style.display = "block";
    } else if (tab === "code") {
      this.tabStorageCode.classList.add("active");
      this.storageCodeView.style.display = "block";
    } else {
      this.tabStorageUploads.classList.add("active");
      this.storageUploadsView.style.display = "block";
    }
    this.fetchStorageFiles();
  }

  async fetchStorageFiles() {
    try {
      const res = await fetch("/api/storage/files");
      const data = await res.json();

      // Audio list
      this.audioFileList.innerHTML = "";
      (data.generated_audio || []).forEach(f => {
        const item = document.createElement("div");
        item.className = "storage-item";
        item.innerHTML = `
          <div class="storage-file-info">
            <span class="storage-file-name">🔊 ${f.name}</span>
            <span class="storage-file-meta">${(f.size_bytes / 1024).toFixed(1)} KB • Synthesized WAV</span>
          </div>
          <button class="btn btn-sm btn-secondary" onclick="new Audio('${f.url}').play()">▶️ Play</button>
        `;
        this.audioFileList.appendChild(item);
      });

      // Code list
      this.codeFileList.innerHTML = "";
      (data.generated_code || []).forEach(f => {
        const item = document.createElement("div");
        item.className = "storage-item";
        item.innerHTML = `
          <div class="storage-file-info">
            <span class="storage-file-name">💻 ${f.name}</span>
            <span class="storage-file-meta">${(f.size_bytes / 1024).toFixed(1)} KB • Python Script</span>
          </div>
          <button class="btn btn-sm btn-primary" onclick="window.neuroApp.executeGeneratedCode('${f.name}')">⚡ Run</button>
        `;
        this.codeFileList.appendChild(item);
      });

      // Uploads list
      this.uploadsFileList.innerHTML = "";
      (data.uploaded_files || []).forEach(f => {
        const item = document.createElement("div");
        item.className = "storage-item";
        item.innerHTML = `
          <div class="storage-file-info">
            <span class="storage-file-name">📄 ${f.name}</span>
            <span class="storage-file-meta">${(f.size_bytes / 1024).toFixed(1)} KB</span>
          </div>
          <a href="${f.url}" download class="btn btn-sm btn-ghost">📥 Download</a>
        `;
        this.uploadsFileList.appendChild(item);
      });
    } catch (e) {
      console.error("Storage fetch error:", e);
    }
  }

  async executeGeneratedCode(filename) {
    try {
      const res = await fetch(`/api/code/execute?filename=${encodeURIComponent(filename)}`, { method: "POST" });
      const data = await res.json();
      alert(`Script Output (${filename}):\n\n${data.output || data.stderr}`);
    } catch (e) {
      console.error("Code execute error:", e);
    }
  }

  // --- Real-Time Test Suite Runner (Instruction 15) ---
  async runSystemTestsSuite() {
    this.executeTestsBtn.disabled = true;
    this.executeTestsBtn.textContent = "⏳ Running Unit & Integration Tests...";
    this.testOutputLog.textContent = "Executing tests/test_system.py against all 15 project instructions...";

    try {
      const res = await fetch("/api/tests/run", { method: "POST" });
      const data = await res.json();
      this.testTotalCount.textContent = data.total_tests;
      this.testPassedStatus.textContent = data.passed ? "PASS" : "FAIL";
      this.testPassedStatus.className = data.passed ? "test-stat-num text-emerald" : "test-stat-num text-rose";
      this.testDurationNum.textContent = `${data.execution_time_seconds}s`;
      this.testOutputLog.textContent = data.output;
    } catch (e) {
      this.testOutputLog.textContent = `Error running tests: ${e}`;
    } finally {
      this.executeTestsBtn.disabled = false;
      this.executeTestsBtn.textContent = "▶️ Re-Run System Evaluation Test Suite";
    }
  }

  // --- Real-Time Telemetry & Core Stream ---
  updatePrivacyUI(enabled) {
    this.isPrivacyBlurEnabled = enabled;
    this.privacyBtnText.textContent = enabled ? "Privacy Blur ON" : "Privacy Blur OFF";
    this.togglePrivacyBtn.className = enabled ? "btn btn-secondary" : "btn btn-ghost";
    this.blurIndicatorTag.textContent = enabled ? "Privacy Blur: ON" : "Privacy Blur: OFF";
    this.blurIndicatorTag.className = enabled ? "tag tag-privacy" : "tag";
    if (this.privacyWatermark) {
      this.privacyWatermark.style.display = enabled ? "block" : "none";
    }
  }

  startTelemetryStream() {
    if (window.EventSource) {
      this.eventSource = new EventSource("/api/telemetry_stream");
      this.eventSource.onmessage = (event) => {
        try {
          const telemetry = JSON.parse(event.data);
          this.handleTelemetryUpdate(telemetry);
        } catch (e) {
          console.error("Failed to parse telemetry event:", e);
        }
      };
      this.eventSource.onerror = () => {
        this.fallbackPoll();
      };
    } else {
      setInterval(() => this.fallbackPoll(), 300);
    }
  }

  async fallbackPoll() {
    try {
      const res = await fetch("/api/telemetry");
      const telemetry = await res.json();
      this.handleTelemetryUpdate(telemetry);
    } catch (e) {}
  }

  handleTelemetryUpdate(t) {
    // 1. Session Timer
    if (t.session_elapsed_seconds !== undefined) {
      const mins = Math.floor(t.session_elapsed_seconds / 60);
      const secs = Math.floor(t.session_elapsed_seconds % 60);
      this.sessionTimer.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    // 2. Engagement Index KPI
    const ei = t.engagement_index || 75.0;
    this.engagementIndexValue.textContent = `${Math.round(ei)}%`;
    this.engagementProgressBar.style.width = `${Math.min(100, Math.max(0, ei))}%`;

    // Trend Badge
    this.engagementTrendBadge.textContent = t.trend || "Stable";
    if (t.trend === "DROPPING") {
      this.engagementTrendBadge.className = "kpi-trend dropping";
    } else {
      this.engagementTrendBadge.className = "kpi-trend";
    }

    // 3. Visual Attention KPI
    const vAtt = t.visual_attention || 80.0;
    this.visualAttentionValue.textContent = `${Math.round(vAtt)}%`;
    this.visualProgressBar.style.width = `${Math.min(100, Math.max(0, vAtt))}%`;

    // 4. Acoustic Dynamics KPI
    const rhythm = t.audio_rhythm || "INSTRUCTOR_MONOLOGUE";
    const formattedRhythm = rhythm.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    this.acousticRhythmValue.textContent = formattedRhythm;

    const rmsWidth = Math.min(100, Math.max(10, (t.audio_energy_rms || 0.04) * 800));
    this.audioEnergyBar.style.width = `${rmsWidth}%`;

    if (rhythm === "INSTRUCTOR_MONOLOGUE" && t.consecutive_monologue_sec) {
      const monoMins = Math.floor(t.consecutive_monologue_sec / 60);
      const monoSecs = Math.floor(t.consecutive_monologue_sec % 60);
      this.monologueDurationSubtext.textContent = `Monologue: ${String(monoMins).padStart(2, '0')}:${String(monoSecs).padStart(2, '0')} • No verbal eavesdropping`;
    } else {
      this.monologueDurationSubtext.textContent = `Acoustic interaction: Active • Offline VAD`;
    }

    // Refresh Activity 3.2 Modal State if open
    if (this.audioAnalysisModal && this.audioAnalysisModal.style.display !== "none") {
      this.updateAudioModalState(t, {
        trend: t.ambient_noise_trend,
        delta_db: t.ambient_noise_delta_db,
        noise_floor_spl: t.noise_floor_spl
      }, t.session_audio_context);
    }

    // Refresh Activity 4.1 Multimodal Agent Modal State if open
    if (this.multimodalAgentModal && !this.multimodalAgentModal.classList.contains("hidden") && t.multimodal_agent) {
      this.updateMultimodalAgentModalState(t.multimodal_agent);
    }

    // Refresh Activity 4.2 Multimodal Signal Fusion Modal State if open
    if (this.fusionActivityModal && !this.fusionActivityModal.classList.contains("hidden")) {
      this.updateFusionActivityModalUI(t);
    }

    // Refresh Activity 4.3 Engagement Scoring Modal State if open
    if (this.scoringActivityModal && !this.scoringActivityModal.classList.contains("hidden") && t.engagement_scoring) {
      this.updateScoringActivityModalUI(t.engagement_scoring);
    }

    // 5. Suggestions
    if (t.latest_suggestion) {
      this.renderSuggestion(t.latest_suggestion);
    }

    // 6. Record for Chart Waveform
    this.telemetryHistory.push({
      time: t.timestamp,
      ei: ei,
      visual: vAtt
    });
    if (this.telemetryHistory.length > this.maxHistoryPoints) {
      this.telemetryHistory.shift();
    }
  }

  renderSuggestion(suggestion) {
    if (!suggestion || !suggestion.title) return;
    const existing = document.querySelector(`[data-suggestion-title="${suggestion.title}"]`);
    if (existing) return;

    const card = document.createElement("div");
    const levelClass = (suggestion.alert_level || "INFO").toLowerCase();
    card.className = `suggestion-card card-${levelClass}`;
    card.setAttribute("data-suggestion-title", suggestion.title);

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    card.innerHTML = `
      <div class="suggestion-header">
        <span class="badge-level level-${levelClass}">${suggestion.alert_level}</span>
        <span class="suggestion-time">${timeStr}</span>
      </div>
      <h3 class="suggestion-title">${suggestion.title}</h3>
      <p class="suggestion-reason">${suggestion.reason}</p>
      <div class="suggestion-action">
        <strong>Suggested Action:</strong> ${suggestion.recommendation}
      </div>
    `;

    this.agentFeed.insertBefore(card, this.agentFeed.firstChild);
    while (this.agentFeed.children.length > 8) {
      this.agentFeed.removeChild(this.agentFeed.lastChild);
    }
  }

  startRosterPolling() {
    this.fetchLiveRoster();
    setInterval(() => this.fetchLiveRoster(), 2000);
  }

  async fetchLiveRoster() {
    try {
      const res = await fetch("/api/attendance/live");
      const data = await res.json();
      this.renderRosterTable(data);
    } catch (e) {
      console.error("Failed to fetch live roster:", e);
    }
  }

  renderRosterTable(data) {
    if (!data || !data.roster) return;
    const roster = data.roster;

    const presentCount = data.present_count || 0;
    const totalCount = data.total_enrolled || roster.length;
    this.presentRatioValue.textContent = `${presentCount} / ${totalCount}`;
    const pct = totalCount > 0 ? Math.round((presentCount / totalCount) * 100) : 0;
    this.attendanceProgressBar.style.width = `${pct}%`;
    this.attendanceRateBadge.textContent = `${pct}% Present`;

    this.rosterTableBody.innerHTML = "";

    roster.forEach(student => {
      const tr = document.createElement("tr");
      const activeMins = Math.floor(student.active_seconds / 60);
      const activeSecs = Math.floor(student.active_seconds % 60);
      const activeStr = `${String(activeMins).padStart(2, '0')}m ${String(activeSecs).padStart(2, '0')}s`;

      const statusClass = `status-${student.status.toLowerCase()}`;
      const liveDotClass = student.is_visible ? "live-dot" : "live-dot inactive";

      const isUnlinked = student.is_unlinked_track || (student.student_id && student.student_id.startsWith("TRK-"));
      const linkBtn = isUnlinked ? `
        <button class="btn btn-sm btn-link-track" onclick="window.neuroApp &amp;&amp; window.neuroApp.openIdentifyModal('${student.student_id}')" title="Link or enroll this live learner" style="margin-left: 6px; font-size: 10px; padding: 2px 7px; background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #38bdf8; border-radius: 4px; cursor: pointer; font-weight: 700;">
          🎯 Identify / Link
        </button>
      ` : '';

      tr.innerHTML = `
        <td class="student-name-cell">
          <span class="${liveDotClass}" title="${student.is_visible ? 'In View' : 'Out of Frame'}"></span>
          <span>${student.display_name}</span>
          ${linkBtn}
        </td>
        <td>${student.seat}</td>
        <td>${activeStr}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 6px;">
            <div class="progress-track" style="width: 50px; height: 4px;">
              <div class="progress-bar progress-cyan" style="width: ${student.presence_ratio}%;"></div>
            </div>
            <span>${student.presence_ratio}%</span>
          </div>
        </td>
        <td><span class="status-badge ${statusClass}">${student.status}</span></td>
      `;
      this.rosterTableBody.appendChild(tr);
    });
  }

  startChartRendering() {
    const draw = () => {
      this.drawEngagementWaveform();
      requestAnimationFrame(draw);
    };
    requestAnimationFrame(draw);
  }

  drawEngagementWaveform() {
    if (!this.ctx || !this.canvas) return;

    // Responsive Canvas Check: sync internal bitmap with rendered CSS dimensions
    const rect = this.canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      const targetW = Math.round(rect.width);
      const targetH = Math.round(rect.height);
      if (this.canvas.width !== targetW || this.canvas.height !== targetH) {
        this.canvas.width = targetW;
        this.canvas.height = targetH;
      }
    }

    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    ctx.lineWidth = 1;
    for (let y = 30; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    if (this.telemetryHistory.length < 2) return;

    const stepX = w / (this.maxHistoryPoints - 1);
    const startOffset = (this.maxHistoryPoints - this.telemetryHistory.length) * stepX;
    const toY = (val) => h - 20 - (val / 100.0) * (h - 40);

    // Visual attention line
    ctx.beginPath();
    ctx.strokeStyle = "#10B981";
    ctx.lineWidth = 2;
    this.telemetryHistory.forEach((pt, i) => {
      const x = startOffset + i * stepX;
      const y = toY(pt.visual);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Engagement line
    ctx.save();
    ctx.shadowColor = "rgba(0, 229, 255, 0.5)";
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.strokeStyle = "#00E5FF";
    ctx.lineWidth = 3;

    this.telemetryHistory.forEach((pt, i) => {
      const x = startOffset + i * stepX;
      const y = toY(pt.ei);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.restore();

    // Glow under engagement line
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "rgba(0, 229, 255, 0.18)");
    grad.addColorStop(1, "rgba(0, 229, 255, 0.0)");

    ctx.lineTo(startOffset + (this.telemetryHistory.length - 1) * stepX, h);
    ctx.lineTo(startOffset, h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Current value dot
    const lastPt = this.telemetryHistory[this.telemetryHistory.length - 1];
    const lastX = startOffset + (this.telemetryHistory.length - 1) * stepX;
    const lastY = toY(lastPt.ei);

    ctx.beginPath();
    ctx.arc(lastX, lastY, 5, 0, Math.PI * 2);
    ctx.fillStyle = "#FFF";
    ctx.shadowColor = "#00E5FF";
    ctx.shadowBlur = 10;
    ctx.fill();
  }

  // -------------------------------------------------------------------------
  // EPIC 6: Activity 6.1 Run Core Application & Pipeline Verification Methods
  // -------------------------------------------------------------------------

  async openCoreAppModal() {
    if (!this.coreAppModal) this.coreAppModal = document.getElementById("coreAppModal");
    if (this.coreAppModal) {
      this._showModal(this.coreAppModal);
      await this.refreshActivity61Status();
    }
  }

  closeCoreAppModal() {
    if (!this.coreAppModal) this.coreAppModal = document.getElementById("coreAppModal");
    if (this.coreAppModal) {
      this._hideModal(this.coreAppModal);
    }
  }

  async refreshActivity61Status() {
    try {
      const res = await fetch("/api/activity_6_1/status");
      const data = await res.json();
      const badge = document.getElementById("activeSourceBadgeModal");
      if (badge && data.active_source) {
        badge.textContent = data.active_source.toUpperCase();
      }
      const verifSourceSelect = document.getElementById("verifSourceSelect");
      if (verifSourceSelect && data.active_source) {
        verifSourceSelect.value = data.active_source;
      }
    } catch (err) {
      console.warn("Could not fetch Activity 6.1 status:", err);
    }
  }

  async switchVideoSourceActivity61(source) {
    try {
      let url = `/api/config/source?source=${source}`;
      if (source === "file") {
        url += `&video_path=storage/uploads/classroom_lecture_sample.mp4`;
      }
      const res = await fetch(url, { method: "POST" });
      const data = await res.json();
      
      const badge = document.getElementById("activeSourceBadgeModal");
      if (badge) badge.textContent = source.toUpperCase();

      if (this.videoSourceSelect) {
        this.videoSourceSelect.value = source;
      }

      const streamImg = document.getElementById("classroomStream");
      if (streamImg) streamImg.src = `/api/video_feed?t=${Date.now()}`;

      // Update card highlighting
      ["Simulated", "File", "Webcam"].forEach(name => {
        const card = document.getElementById(`sourceCard${name}`);
        if (card) {
          if (name.toLowerCase() === source.toLowerCase()) {
            card.style.borderColor = "#c084fc";
            card.style.boxShadow = "0 0 14px rgba(192, 132, 252, 0.35)";
          } else {
            card.style.borderColor = "rgba(148, 163, 184, 0.2)";
            card.style.boxShadow = "none";
          }
        }
      });
    } catch (err) {
      console.error("Failed to switch video source:", err);
    }
  }

  async triggerPipelineVerification() {
    const runBtn = document.getElementById("runVerifBtn");
    const loader = document.getElementById("verifLoadingIndicator");
    const resultsContainer = document.getElementById("verifResultsContainer");
    const sourceSelect = document.getElementById("verifSourceSelect");
    const framesSelect = document.getElementById("verifFrameCount");

    const source = sourceSelect ? sourceSelect.value : "simulated";
    const frames = framesSelect ? parseInt(framesSelect.value, 10) : 5;

    if (runBtn) runBtn.disabled = true;
    if (loader) loader.style.display = "block";
    if (resultsContainer) resultsContainer.style.display = "none";

    try {
      let url = `/api/activity_6_1/verify_pipeline?source=${source}&num_frames=${frames}`;
      if (source === "file") {
        url += `&video_path=storage/uploads/classroom_lecture_sample.mp4`;
      }
      const res = await fetch(url, { method: "POST" });
      const result = await res.json();

      // Render results
      const statusEl = document.getElementById("verifStatusText");
      const fpsEl = document.getElementById("verifFpsText");
      const elapsedEl = document.getElementById("verifElapsedText");
      const framesEl = document.getElementById("verifFramesText");
      const tbody = document.getElementById("verifModulesTableBody");
      const rawPre = document.getElementById("verifRawJsonPre");

      if (statusEl) statusEl.textContent = result.status || "SUCCESS";
      if (fpsEl) fpsEl.textContent = `${result.throughput_fps || 0.0} FPS`;
      if (elapsedEl) elapsedEl.textContent = `${result.elapsed_seconds || 0.0} sec`;
      if (framesEl) framesEl.textContent = `${result.total_frames_processed || frames} Frames`;

      if (rawPre) rawPre.textContent = JSON.stringify(result, null, 2);

      if (tbody && result.modules_verified) {
        tbody.innerHTML = "";
        const modTitles = {
          "vision_processing": { title: "1. Vision Processing", icon: "👁️" },
          "audio_analysis": { title: "2. Audio Analysis", icon: "🎙️" },
          "multimodal_fusion": { title: "3. Multimodal Signal Fusion", icon: "🎛️" },
          "engagement_scoring": { title: "4. Engagement Scoring Logic", icon: "📈" },
          "analytics_generation": { title: "5. Analytics & Suggestions", icon: "💡" }
        };

        Object.keys(result.modules_verified).forEach(key => {
          const mod = result.modules_verified[key];
          const info = modTitles[key] || { title: key, icon: "⚙️" };
          const row = document.createElement("tr");
          row.style.borderBottom = "1px solid rgba(148, 163, 184, 0.1)";

          let evidenceHtml = "";
          if (key === "vision_processing") {
            evidenceHtml = `Faces: ${mod.faces_detected_last_frame} | Visual Att: ${(mod.average_visual_attention * 100).toFixed(0)}%`;
          } else if (key === "audio_analysis") {
            evidenceHtml = `SPL: ${mod.noise_spl_db} dB | State: ${mod.speech_state} | VAD: ${mod.vad_active ? "Active" : "Silent"}`;
          } else if (key === "multimodal_fusion") {
            evidenceHtml = `Jitter: ${mod.sync_jitter_ms}ms | EI: ${mod.engagement_index} | Corr: ${mod.cross_modal_correlation}`;
          } else if (key === "engagement_scoring") {
            evidenceHtml = `Composite: ${mod.composite_score}% | Tier: ${mod.engagement_level}`;
          } else if (key === "analytics_generation") {
            evidenceHtml = `Suggestions: ${mod.recommendations_count} | Student: ${mod.student_analyzed} (Consistency: ${mod.consistency_score}%)`;
          }

          row.innerHTML = `
            <td style="padding: 8px; font-weight: 700; color: #f1f5f9;">
              ${info.icon} ${info.title}
            </td>
            <td style="padding: 8px;">
              <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: 700;">
                VERIFIED
              </span>
            </td>
            <td style="padding: 8px; color: #38bdf8; font-family: monospace; font-size: 10px;">
              ${evidenceHtml}
            </td>
            <td style="padding: 8px; color: #94a3b8; font-size: 11px;">
              ${mod.summary}
            </td>
          `;
          tbody.appendChild(row);
        });
      }

      // Update pipeline stepper indicators to VERIFIED
      for (let i = 1; i <= 5; i++) {
        const stepStatus = document.getElementById(`pipeMod${i}Status`);
        if (stepStatus) {
          stepStatus.textContent = "VERIFIED";
          stepStatus.style.color = "#34d399";
        }
      }

      if (resultsContainer) resultsContainer.style.display = "block";
    } catch (err) {
      console.error("Pipeline verification failed:", err);
      alert("Pipeline verification error: " + err.message);
    } finally {
      if (runBtn) runBtn.disabled = false;
      if (loader) loader.style.display = "none";
    }
  }

  // --- Activity Explorer Dropdown Controller ---
  toggleActivityDropdown(e) {
    if (e) e.stopPropagation();
    const menu = document.getElementById("activityDropdownMenu");
    if (menu) {
      menu.classList.toggle("show");
    }
  }

  // --- 3-Way Hybrid Student Enrollment & Webcam Linking Methods ---
  async openIdentifyModal(trackId) {
    this.activeIdentifyTrackId = trackId;
    if (this.identifyTrackBadge) this.identifyTrackBadge.textContent = trackId;
    if (this.identifyModalTrackId) this.identifyModalTrackId.textContent = trackId;

    if (this.identifyStatusBanner) {
      this.identifyStatusBanner.style.display = "none";
      this.identifyStatusBanner.textContent = "";
    }

    // Set face crop
    if (this.identifyFaceCropImg && this.identifyFaceCropFallback) {
      this.identifyFaceCropImg.style.display = "none";
      this.identifyFaceCropFallback.style.display = "block";
      this.identifyFaceCropImg.onload = () => {
        this.identifyFaceCropImg.style.display = "block";
        this.identifyFaceCropFallback.style.display = "none";
      };
      this.identifyFaceCropImg.onerror = () => {
        this.identifyFaceCropImg.style.display = "none";
        this.identifyFaceCropFallback.style.display = "block";
      };
      this.identifyFaceCropImg.src = `/api/attendance/track_crop/${encodeURIComponent(trackId)}?t=${Date.now()}`;
    }

    // Reset inputs
    if (this.newStudentId) this.newStudentId.value = "";
    if (this.newStudentName) this.newStudentName.value = "";
    if (this.newStudentSeat) this.newStudentSeat.value = "";
    if (this.newStudentPhotoUpload) this.newStudentPhotoUpload.value = "";

    // Fetch enrolled students for dropdown
    try {
      const res = await fetch("/api/attendance/enrolled_students");
      const data = await res.json();
      if (this.existingStudentSelect && data && data.students) {
        this.existingStudentSelect.innerHTML = '<option value="">-- Choose a student from database --</option>';
        data.students.forEach(s => {
          const opt = document.createElement("option");
          opt.value = s.student_id;
          opt.textContent = `${s.name} (${s.student_id}) - ${s.seat || 'No Seat'}`;
          this.existingStudentSelect.appendChild(opt);
        });
      }
    } catch (err) {
      console.warn("Could not fetch enrolled students:", err);
    }

    this.setIdentifyMode("existing");
    this._showModal(this.identifyModal);
  }

  closeIdentifyModal() {
    this._hideModal(this.identifyModal);
    this.activeIdentifyTrackId = null;
  }

  setIdentifyMode(mode) {
    this.identifyMode = mode;
    if (mode === "existing") {
      if (this.tabLinkExisting) {
        this.tabLinkExisting.style.borderColor = "#38bdf8";
        this.tabLinkExisting.style.background = "rgba(56, 189, 248, 0.15)";
        this.tabLinkExisting.style.color = "#38bdf8";
      }
      if (this.tabEnrollNew) {
        this.tabEnrollNew.style.borderColor = "rgba(148, 163, 184, 0.2)";
        this.tabEnrollNew.style.background = "transparent";
        this.tabEnrollNew.style.color = "#94a3b8";
      }
      if (this.sectionLinkExisting) this.sectionLinkExisting.style.display = "block";
      if (this.sectionEnrollNew) this.sectionEnrollNew.style.display = "none";
    } else {
      if (this.tabEnrollNew) {
        this.tabEnrollNew.style.borderColor = "#38bdf8";
        this.tabEnrollNew.style.background = "rgba(56, 189, 248, 0.15)";
        this.tabEnrollNew.style.color = "#38bdf8";
      }
      if (this.tabLinkExisting) {
        this.tabLinkExisting.style.borderColor = "rgba(148, 163, 184, 0.2)";
        this.tabLinkExisting.style.background = "transparent";
        this.tabLinkExisting.style.color = "#94a3b8";
      }
      if (this.sectionLinkExisting) this.sectionLinkExisting.style.display = "none";
      if (this.sectionEnrollNew) this.sectionEnrollNew.style.display = "block";
    }
  }

  async submitIdentityLink() {
    if (!this.activeIdentifyTrackId) return;

    let targetStudentId = "";
    let newStudentName = null;
    let newStudentSeat = null;
    let customImageB64 = null;

    if (this.identifyMode === "existing") {
      targetStudentId = this.existingStudentSelect ? this.existingStudentSelect.value : "";
      if (!targetStudentId) {
        this.showIdentifyBanner("Please select an enrolled student from the dropdown list.", "error");
        return;
      }
    } else {
      targetStudentId = this.newStudentId ? this.newStudentId.value.trim() : "";
      newStudentName = this.newStudentName ? this.newStudentName.value.trim() : "";
      newStudentSeat = this.newStudentSeat ? this.newStudentSeat.value.trim() : "";

      if (!targetStudentId || !newStudentName) {
        this.showIdentifyBanner("Please provide both a Student ID (e.g., STU-109) and Full Name.", "error");
        return;
      }

      // Check optional file upload
      if (this.newStudentPhotoUpload && this.newStudentPhotoUpload.files && this.newStudentPhotoUpload.files[0]) {
        try {
          const file = this.newStudentPhotoUpload.files[0];
          customImageB64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
          });
        } catch (e) {
          console.warn("Could not read uploaded photo:", e);
        }
      }
    }

    if (this.btnSubmitIdentity) {
      this.btnSubmitIdentity.disabled = true;
      this.btnSubmitIdentity.textContent = "Linking Biometric Identity...";
    }

    try {
      const payload = {
        track_id: this.activeIdentifyTrackId,
        target_student_id: targetStudentId,
        new_student_name: newStudentName,
        new_student_seat: newStudentSeat,
        custom_image_b64: customImageB64
      };

      const res = await fetch("/api/attendance/link_track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.ok && data.status === "SUCCESS") {
        this.showIdentifyBanner(`✓ Successfully linked to ${data.linked_name} (${data.linked_student_id})! Merged active presence.`, "success");
        this.fetchLiveRoster();
        this.fetchDetailedAttendanceLogs();
        this.showToast(`Biometric link established: ${data.linked_name} (${data.linked_student_id})`, "success");
        setTimeout(() => {
          this.closeIdentifyModal();
          if (this.btnSubmitIdentity) {
            this.btnSubmitIdentity.disabled = false;
            this.btnSubmitIdentity.textContent = "✓ Confirm & Link Identity";
          }
        }, 1200);
      } else {
        this.showIdentifyBanner(`Error: ${data.message || 'Linking failed'}`, "error");
        if (this.btnSubmitIdentity) {
          this.btnSubmitIdentity.disabled = false;
          this.btnSubmitIdentity.textContent = "✓ Confirm & Link Identity";
        }
      }
    } catch (err) {
      console.error("Link identity request error:", err);
      this.showIdentifyBanner(`Network error: ${err.message}`, "error");
      if (this.btnSubmitIdentity) {
        this.btnSubmitIdentity.disabled = false;
        this.btnSubmitIdentity.textContent = "✓ Confirm & Link Identity";
      }
    }
  }

  showIdentifyBanner(msg, type) {
    if (!this.identifyStatusBanner) return;
    this.identifyStatusBanner.style.display = "flex";
    this.identifyStatusBanner.style.alignItems = "center";
    this.identifyStatusBanner.style.gap = "8px";
    this.identifyStatusBanner.style.fontWeight = "600";
    this.identifyStatusBanner.style.borderRadius = "8px";
    this.identifyStatusBanner.style.padding = "10px 14px";
    this.identifyStatusBanner.style.fontSize = "12px";
    this.identifyStatusBanner.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.3)";

    if (type === "success") {
      this.identifyStatusBanner.innerHTML = `<span>✅</span> <span>${msg}</span>`;
      this.identifyStatusBanner.style.background = "rgba(16, 185, 129, 0.25)";
      this.identifyStatusBanner.style.border = "1px solid rgba(52, 211, 153, 0.6)";
      this.identifyStatusBanner.style.color = "#34d399";
    } else {
      this.identifyStatusBanner.innerHTML = `<span>⚠️</span> <span>${msg}</span>`;
      this.identifyStatusBanner.style.background = "rgba(239, 68, 68, 0.25)";
      this.identifyStatusBanner.style.border = "1px solid rgba(248, 113, 113, 0.6)";
      this.identifyStatusBanner.style.color = "#fca5a5";
    }
  }

  async resetToLiveTelemetry() {
    try {
      await this.resetRecommendationCooldowns();
      await this.triggerEvaluationNow();
      if (this.fusionCustomModalitiesList) {
        this.fusionCustomModalitiesList.innerHTML = `
          <span class="badge-tag" style="background: rgba(30, 41, 59, 0.8); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);">
            Modality: Vision (Primary)
          </span>
          <span class="badge-tag" style="background: rgba(30, 41, 59, 0.8); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.3);">
            Modality: Audio (Primary)
          </span>
          <span id="customModalityTag" class="badge-tag" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">
            Extensible Hook: Ready
          </span>
        `;
      }
      this.fetchLiveRoster();
    } catch (e) {
      console.warn("Failed to reset to live telemetry:", e);
    }
  }
}

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  window.neuroApp = new DashboardController();
});
