// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'G777 AI Orchestrator';

  @override
  String get dashboard => 'Dashboard';

  @override
  String get campaigns => 'Campaigns';

  @override
  String get sent => 'Sent';

  @override
  String get failed => 'Failed';

  @override
  String get pending => 'Pending';

  @override
  String get contacts => 'Contacts';

  @override
  String get settings => 'Settings';

  @override
  String get whatsappStatus => 'WhatsApp Status';

  @override
  String get connected => 'Connected';

  @override
  String get disconnected => 'Disconnected';

  @override
  String get initializePairing => 'INITIALIZE PAIRING';

  @override
  String get refreshStatus => 'Refresh Status';

  @override
  String get liveTelemetry => 'Live Telemetry';

  @override
  String get activeSessions => 'Active Sessions';

  @override
  String get uptime => 'Uptime';

  @override
  String get changeLanguage => 'Language';

  @override
  String get ready => 'READY';

  @override
  String get standby => 'STANDBY';

  @override
  String get active => 'ACTIVE';

  @override
  String get live => 'LIVE';

  @override
  String get whatsappLinked => 'WHATSAPP LINKED';

  @override
  String get whatsappDisconnected => 'WHATSAPP DISCONNECTED';

  @override
  String get status => 'STATUS';

  @override
  String get online => 'ONLINE';

  @override
  String get close => 'CLOSE';

  @override
  String get categoryA => '-A Advanced Sender';

  @override
  String get featureA1 => '-1 Attachments';

  @override
  String get featureA2 => 'Variables';

  @override
  String get categoryB => '-B Group Tools';

  @override
  String get featureB1 => 'Group Members Grabber-1';

  @override
  String get featureB2 => 'Group Links Grabber-2';

  @override
  String get featureB3 => 'Auto Group Joiner-3';

  @override
  String get categoryC => '-C Data Tools';

  @override
  String get featureC1 => 'Google Maps Data Extractor-1';

  @override
  String get featureC2 => 'Social Media Extractor-2';

  @override
  String get categoryD => '-D Utilities';

  @override
  String get featureD1 => 'Number Filter-1';

  @override
  String get featureD2 => 'Warmer-2';

  @override
  String get featureD3 => 'Poll Sender-3';

  @override
  String get featureD4 => 'Opportunity hunter-4';

  @override
  String get navSender => 'Advanced Sender';

  @override
  String get navGroupTools => 'Group Tools';

  @override
  String get navDataTools => 'Data Tools';

  @override
  String get navUtilities => 'Utilities';

  @override
  String get navFilter => 'Number Filter';

  @override
  String get navWarmer => 'Warmer';

  @override
  String get navHunter => 'Opportunity Hunter';

  @override
  String get navPoll => 'Poll Sender';

  @override
  String get navCloud => 'Dashboard';

  @override
  String get navBusiness => 'Settings';

  @override
  String get catAdvancedSender => 'ADVANCED SENDER';

  @override
  String get catGroupTools => 'GROUP TOOLS';

  @override
  String get catDataTools => 'DATA TOOLS';

  @override
  String get catUtilities => 'UTILITIES';

  @override
  String get lblMembersGrabber => 'Members Grabber';

  @override
  String get lblLinksGrabber => 'Links Grabber';

  @override
  String get lblGoogleMaps => 'Google Maps';

  @override
  String get lblSocialMedia => 'Social Media';

  @override
  String get lblOppHunter => 'Opp. Hunter';

  @override
  String get navThemes => 'Themes';

  @override
  String get orchestrationTerminal => 'ORCHESTRATION TERMINAL';

  @override
  String get secureStorage => 'SECURE STORAGE';

  @override
  String get portDiscovery => 'PORT DISCOVERY';

  @override
  String get aiCore => 'AI CORE';

  @override
  String get telemetry => 'TELEMETRY';

  @override
  String get visualEngine => 'Visual Engine';

  @override
  String get neonPink => 'Neon Pink';

  @override
  String get cyberBlue => 'Cyber Blue';

  @override
  String get industrial => 'Industrial';

  @override
  String get instance => 'Instance';

  @override
  String get systemStandby => 'SYSTEM STANDBY';

  @override
  String get disconnectInstance => 'Disconnect Instance';

  @override
  String get pairingDialogTitle => 'WHATSAPP PAIRING';

  @override
  String get qrCode => 'QR Code';

  @override
  String get phoneNumber => 'Phone Number';

  @override
  String get phoneLabel => 'Phone Number with Country Code';

  @override
  String get phoneHint => 'e.g. 971501234567';

  @override
  String get generateCode => 'GENERATE PAIRING CODE';

  @override
  String get pairingCodeInstructions =>
      'Enter this code on your phone in Linked Devices > Link with Phone Number';

  @override
  String get qrInstructions => 'Scan this QR code using WhatsApp on your phone';

  @override
  String get groupSender => 'Group Sender';

  @override
  String get excelDataFeed => 'EXCEL DATA FEED';

  @override
  String get chooseDataSource => 'CHOOSE DATA SOURCE';

  @override
  String readyFile(String fileName) {
    return 'Ready: $fileName';
  }

  @override
  String get targetSegment => 'TARGET SEGMENT';

  @override
  String get selectDataSheet => 'Select Data Sheet';

  @override
  String contactsCount(int count) {
    return '$count Contacts';
  }

  @override
  String get campaignSettings => 'CAMPAIGN SETTINGS';

  @override
  String msgVariant(int index) {
    return 'Msg Variant $index';
  }

  @override
  String typeMsgVariant(int index) {
    return 'Type Msg Variant $index';
  }

  @override
  String variableHelper(String name) {
    return 'Helper: $name';
  }

  @override
  String get mediaAttached => 'MEDIA ATTACHED';

  @override
  String get attachMedia => 'ATTACH MEDIA';

  @override
  String get groupLinkOptional => 'Group Link (Optional Join)';

  @override
  String get minDelay => 'Min Delay (sec)';

  @override
  String get maxDelay => 'Max Delay (sec)';

  @override
  String get launchCampaign => 'LAUNCH CAMPAIGN';

  @override
  String get executingCampaign => 'EXECUTING CAMPAIGN';

  @override
  String get operationComplete => 'OPERATION COMPLETE';

  @override
  String get dataGrabber => 'Members Grabber';

  @override
  String get extractMemberDesc =>
      'Extract all active members from any WhatsApp group you belong to.';

  @override
  String get targetGroups => 'TARGET GROUPS';

  @override
  String get membersStream => 'MEMBERS STREAM';

  @override
  String get noDataStreaming => 'No data streaming yet.';

  @override
  String get numberValidator => 'Number Filter';

  @override
  String get numberValidatorDesc =>
      'Verify phone numbers and filter out corrupt or non-whatsapp accounts.';

  @override
  String get readyForScanning => 'READY FOR SCANNING';

  @override
  String get scanResults => 'SCAN RESULTS';

  @override
  String get totalScanned => 'TOTAL SCANNED';

  @override
  String get validAccounts => 'VALID ACCOUNTS';

  @override
  String get corruptMissing => 'CORRUPT/MISSING';

  @override
  String get accountWarmer => 'Account Warmer';

  @override
  String get accountWarmerDesc =>
      'Simulate natural conversation between two accounts to build trust.';

  @override
  String get phoneJid1 => 'PHONE JID 1';

  @override
  String get phoneJid2 => 'PHONE JID 2';

  @override
  String get totalMessages => 'TOTAL MESSAGES';

  @override
  String get averageDelay => 'AVG DELAY (SEC)';

  @override
  String get terminateWarming => 'TERMINATE WARMING';

  @override
  String get startWarming => 'START WARMING';

  @override
  String get warmingTelemetry => 'WARMING TELEMETRY';

  @override
  String get noActivity => 'No activity yet.';

  @override
  String get systemThemeMode => 'System Theme Mode';

  @override
  String get cyberpunkSFX => 'Cyberpunk SFX';

  @override
  String get enableSFX => 'Enable Sound Effects';

  @override
  String get languageIntegration => 'Language Integration';

  @override
  String switchLanguage(String lang) {
    return 'Switch to $lang';
  }

  @override
  String get connectivityNode => 'CONNECTIVITY NODE';

  @override
  String get evolutionApiHost => 'Evolution API Host';

  @override
  String get globalMasterKey => 'Global Master Key';

  @override
  String get nodeHealthStatus => 'Node Health Status';

  @override
  String get pingServer => 'PING SERVER';

  @override
  String get safetyProtocols => 'SAFETY PROTOCOLS';

  @override
  String messageBatchDelay(int min, int max) {
    return 'Delay: ${min}s - ${max}s';
  }

  @override
  String get dailyTransmissionLimit => 'Daily Transmission Limit';

  @override
  String get aiPersonaEngine => 'AI PERSONA ENGINE';

  @override
  String get coreModel => 'Core Reasoning Model';

  @override
  String get creativityThreshold => 'Creativity Threshold';

  @override
  String get osVersion => 'OS VERSION';

  @override
  String get navGrabber => 'Members Grabber';

  @override
  String get navLinks => 'Links Grabber';

  @override
  String swapLanguageToast(String locale) {
    return 'System Language: $locale';
  }

  @override
  String get systemLogs => 'SYSTEM LOGS';

  @override
  String get awaitingCommands => 'Awaiting Commands...';

  @override
  String get groupSenderTitle => 'Group Sender';

  @override
  String get startSending => 'START SENDING';

  @override
  String get logs => 'LOGS';

  @override
  String get typeMessage => 'Type Message...';

  @override
  String get engineSettings => 'ENGINE SETTINGS';

  @override
  String get running => 'RUNNING';

  @override
  String get connection => 'Connection';

  @override
  String get googleMaps => 'Google Maps';

  @override
  String get crmDashboard => 'CRM Dashboard';

  @override
  String get opportunityHunter => 'Opportunity Hunter';

  @override
  String get businessSettings => 'Business Settings';

  @override
  String get aiAssistant => 'AI Assistant';

  @override
  String get cloudServer => 'Cloud Server';

  @override
  String get themeSettings => 'Theme Settings';

  @override
  String get membersGrabber => 'Members Grabber';

  @override
  String get linksGrabber => 'Links Grabber';

  @override
  String get numberFilter => 'Number Filter';

  @override
  String get import => 'Import';

  @override
  String get fileUpload => 'File Upload';

  @override
  String get campaignContent => 'Campaign Content';

  @override
  String get groupLink => 'Group Link';
}
