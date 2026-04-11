import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('en'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'G777 AI Orchestrator'**
  String get appTitle;

  /// No description provided for @dashboard.
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get dashboard;

  /// No description provided for @campaigns.
  ///
  /// In en, this message translates to:
  /// **'Campaigns'**
  String get campaigns;

  /// No description provided for @sent.
  ///
  /// In en, this message translates to:
  /// **'Sent'**
  String get sent;

  /// No description provided for @failed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get failed;

  /// No description provided for @pending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get pending;

  /// No description provided for @contacts.
  ///
  /// In en, this message translates to:
  /// **'Contacts'**
  String get contacts;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @whatsappStatus.
  ///
  /// In en, this message translates to:
  /// **'WhatsApp Status'**
  String get whatsappStatus;

  /// No description provided for @connected.
  ///
  /// In en, this message translates to:
  /// **'Connected'**
  String get connected;

  /// No description provided for @disconnected.
  ///
  /// In en, this message translates to:
  /// **'Disconnected'**
  String get disconnected;

  /// No description provided for @initializePairing.
  ///
  /// In en, this message translates to:
  /// **'INITIALIZE PAIRING'**
  String get initializePairing;

  /// No description provided for @refreshStatus.
  ///
  /// In en, this message translates to:
  /// **'Refresh Status'**
  String get refreshStatus;

  /// No description provided for @liveTelemetry.
  ///
  /// In en, this message translates to:
  /// **'Live Telemetry'**
  String get liveTelemetry;

  /// No description provided for @activeSessions.
  ///
  /// In en, this message translates to:
  /// **'Active Sessions'**
  String get activeSessions;

  /// No description provided for @uptime.
  ///
  /// In en, this message translates to:
  /// **'Uptime'**
  String get uptime;

  /// No description provided for @changeLanguage.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get changeLanguage;

  /// No description provided for @ready.
  ///
  /// In en, this message translates to:
  /// **'READY'**
  String get ready;

  /// No description provided for @standby.
  ///
  /// In en, this message translates to:
  /// **'STANDBY'**
  String get standby;

  /// No description provided for @active.
  ///
  /// In en, this message translates to:
  /// **'ACTIVE'**
  String get active;

  /// No description provided for @live.
  ///
  /// In en, this message translates to:
  /// **'LIVE'**
  String get live;

  /// No description provided for @whatsappLinked.
  ///
  /// In en, this message translates to:
  /// **'WHATSAPP LINKED'**
  String get whatsappLinked;

  /// No description provided for @whatsappDisconnected.
  ///
  /// In en, this message translates to:
  /// **'WHATSAPP DISCONNECTED'**
  String get whatsappDisconnected;

  /// No description provided for @status.
  ///
  /// In en, this message translates to:
  /// **'STATUS'**
  String get status;

  /// No description provided for @online.
  ///
  /// In en, this message translates to:
  /// **'ONLINE'**
  String get online;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'CLOSE'**
  String get close;

  /// No description provided for @categoryA.
  ///
  /// In en, this message translates to:
  /// **'-A Advanced Sender'**
  String get categoryA;

  /// No description provided for @featureA1.
  ///
  /// In en, this message translates to:
  /// **'-1 Attachments'**
  String get featureA1;

  /// No description provided for @featureA2.
  ///
  /// In en, this message translates to:
  /// **'Variables'**
  String get featureA2;

  /// No description provided for @categoryB.
  ///
  /// In en, this message translates to:
  /// **'-B Group Tools'**
  String get categoryB;

  /// No description provided for @featureB1.
  ///
  /// In en, this message translates to:
  /// **'Group Members Grabber-1'**
  String get featureB1;

  /// No description provided for @featureB2.
  ///
  /// In en, this message translates to:
  /// **'Group Links Grabber-2'**
  String get featureB2;

  /// No description provided for @featureB3.
  ///
  /// In en, this message translates to:
  /// **'Auto Group Joiner-3'**
  String get featureB3;

  /// No description provided for @categoryC.
  ///
  /// In en, this message translates to:
  /// **'-C Data Tools'**
  String get categoryC;

  /// No description provided for @featureC1.
  ///
  /// In en, this message translates to:
  /// **'Google Maps Data Extractor-1'**
  String get featureC1;

  /// No description provided for @featureC2.
  ///
  /// In en, this message translates to:
  /// **'Social Media Extractor-2'**
  String get featureC2;

  /// No description provided for @categoryD.
  ///
  /// In en, this message translates to:
  /// **'-D Utilities'**
  String get categoryD;

  /// No description provided for @featureD1.
  ///
  /// In en, this message translates to:
  /// **'Number Filter-1'**
  String get featureD1;

  /// No description provided for @featureD2.
  ///
  /// In en, this message translates to:
  /// **'Warmer-2'**
  String get featureD2;

  /// No description provided for @featureD3.
  ///
  /// In en, this message translates to:
  /// **'Poll Sender-3'**
  String get featureD3;

  /// No description provided for @featureD4.
  ///
  /// In en, this message translates to:
  /// **'Opportunity hunter-4'**
  String get featureD4;

  /// No description provided for @navSender.
  ///
  /// In en, this message translates to:
  /// **'Advanced Sender'**
  String get navSender;

  /// No description provided for @navGroupTools.
  ///
  /// In en, this message translates to:
  /// **'Group Tools'**
  String get navGroupTools;

  /// No description provided for @navDataTools.
  ///
  /// In en, this message translates to:
  /// **'Data Tools'**
  String get navDataTools;

  /// No description provided for @navUtilities.
  ///
  /// In en, this message translates to:
  /// **'Utilities'**
  String get navUtilities;

  /// No description provided for @navFilter.
  ///
  /// In en, this message translates to:
  /// **'Number Filter'**
  String get navFilter;

  /// No description provided for @navWarmer.
  ///
  /// In en, this message translates to:
  /// **'Warmer'**
  String get navWarmer;

  /// No description provided for @navHunter.
  ///
  /// In en, this message translates to:
  /// **'Opportunity Hunter'**
  String get navHunter;

  /// No description provided for @navPoll.
  ///
  /// In en, this message translates to:
  /// **'Poll Sender'**
  String get navPoll;

  /// No description provided for @navCloud.
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get navCloud;

  /// No description provided for @navBusiness.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get navBusiness;

  /// No description provided for @catAdvancedSender.
  ///
  /// In en, this message translates to:
  /// **'ADVANCED SENDER'**
  String get catAdvancedSender;

  /// No description provided for @catGroupTools.
  ///
  /// In en, this message translates to:
  /// **'GROUP TOOLS'**
  String get catGroupTools;

  /// No description provided for @catDataTools.
  ///
  /// In en, this message translates to:
  /// **'DATA TOOLS'**
  String get catDataTools;

  /// No description provided for @catUtilities.
  ///
  /// In en, this message translates to:
  /// **'UTILITIES'**
  String get catUtilities;

  /// No description provided for @lblMembersGrabber.
  ///
  /// In en, this message translates to:
  /// **'Members Grabber'**
  String get lblMembersGrabber;

  /// No description provided for @lblLinksGrabber.
  ///
  /// In en, this message translates to:
  /// **'Links Grabber'**
  String get lblLinksGrabber;

  /// No description provided for @lblGoogleMaps.
  ///
  /// In en, this message translates to:
  /// **'Google Maps'**
  String get lblGoogleMaps;

  /// No description provided for @lblSocialMedia.
  ///
  /// In en, this message translates to:
  /// **'Social Media'**
  String get lblSocialMedia;

  /// No description provided for @lblOppHunter.
  ///
  /// In en, this message translates to:
  /// **'Opp. Hunter'**
  String get lblOppHunter;

  /// No description provided for @navThemes.
  ///
  /// In en, this message translates to:
  /// **'Themes'**
  String get navThemes;

  /// No description provided for @orchestrationTerminal.
  ///
  /// In en, this message translates to:
  /// **'ORCHESTRATION TERMINAL'**
  String get orchestrationTerminal;

  /// No description provided for @secureStorage.
  ///
  /// In en, this message translates to:
  /// **'SECURE STORAGE'**
  String get secureStorage;

  /// No description provided for @portDiscovery.
  ///
  /// In en, this message translates to:
  /// **'PORT DISCOVERY'**
  String get portDiscovery;

  /// No description provided for @aiCore.
  ///
  /// In en, this message translates to:
  /// **'AI CORE'**
  String get aiCore;

  /// No description provided for @telemetry.
  ///
  /// In en, this message translates to:
  /// **'TELEMETRY'**
  String get telemetry;

  /// No description provided for @visualEngine.
  ///
  /// In en, this message translates to:
  /// **'Visual Engine'**
  String get visualEngine;

  /// No description provided for @neonPink.
  ///
  /// In en, this message translates to:
  /// **'Neon Pink'**
  String get neonPink;

  /// No description provided for @cyberBlue.
  ///
  /// In en, this message translates to:
  /// **'Cyber Blue'**
  String get cyberBlue;

  /// No description provided for @industrial.
  ///
  /// In en, this message translates to:
  /// **'Industrial'**
  String get industrial;

  /// No description provided for @instance.
  ///
  /// In en, this message translates to:
  /// **'Instance'**
  String get instance;

  /// No description provided for @systemStandby.
  ///
  /// In en, this message translates to:
  /// **'SYSTEM STANDBY'**
  String get systemStandby;

  /// No description provided for @disconnectInstance.
  ///
  /// In en, this message translates to:
  /// **'Disconnect Instance'**
  String get disconnectInstance;

  /// No description provided for @pairingDialogTitle.
  ///
  /// In en, this message translates to:
  /// **'WHATSAPP PAIRING'**
  String get pairingDialogTitle;

  /// No description provided for @qrCode.
  ///
  /// In en, this message translates to:
  /// **'QR Code'**
  String get qrCode;

  /// No description provided for @phoneNumber.
  ///
  /// In en, this message translates to:
  /// **'Phone Number'**
  String get phoneNumber;

  /// No description provided for @phoneLabel.
  ///
  /// In en, this message translates to:
  /// **'Phone Number with Country Code'**
  String get phoneLabel;

  /// No description provided for @phoneHint.
  ///
  /// In en, this message translates to:
  /// **'e.g. 971501234567'**
  String get phoneHint;

  /// No description provided for @generateCode.
  ///
  /// In en, this message translates to:
  /// **'GENERATE PAIRING CODE'**
  String get generateCode;

  /// No description provided for @pairingCodeInstructions.
  ///
  /// In en, this message translates to:
  /// **'Enter this code on your phone in Linked Devices > Link with Phone Number'**
  String get pairingCodeInstructions;

  /// No description provided for @qrInstructions.
  ///
  /// In en, this message translates to:
  /// **'Scan this QR code using WhatsApp on your phone'**
  String get qrInstructions;

  /// No description provided for @groupSender.
  ///
  /// In en, this message translates to:
  /// **'Group Sender'**
  String get groupSender;

  /// No description provided for @excelDataFeed.
  ///
  /// In en, this message translates to:
  /// **'EXCEL DATA FEED'**
  String get excelDataFeed;

  /// No description provided for @chooseDataSource.
  ///
  /// In en, this message translates to:
  /// **'CHOOSE DATA SOURCE'**
  String get chooseDataSource;

  /// No description provided for @readyFile.
  ///
  /// In en, this message translates to:
  /// **'Ready: {fileName}'**
  String readyFile(String fileName);

  /// No description provided for @targetSegment.
  ///
  /// In en, this message translates to:
  /// **'TARGET SEGMENT'**
  String get targetSegment;

  /// No description provided for @selectDataSheet.
  ///
  /// In en, this message translates to:
  /// **'Select Data Sheet'**
  String get selectDataSheet;

  /// No description provided for @contactsCount.
  ///
  /// In en, this message translates to:
  /// **'{count} Contacts'**
  String contactsCount(int count);

  /// No description provided for @campaignSettings.
  ///
  /// In en, this message translates to:
  /// **'CAMPAIGN SETTINGS'**
  String get campaignSettings;

  /// No description provided for @msgVariant.
  ///
  /// In en, this message translates to:
  /// **'Msg Variant {index}'**
  String msgVariant(int index);

  /// No description provided for @typeMsgVariant.
  ///
  /// In en, this message translates to:
  /// **'Type Msg Variant {index}'**
  String typeMsgVariant(int index);

  /// No description provided for @variableHelper.
  ///
  /// In en, this message translates to:
  /// **'Helper: {name}'**
  String variableHelper(String name);

  /// No description provided for @mediaAttached.
  ///
  /// In en, this message translates to:
  /// **'MEDIA ATTACHED'**
  String get mediaAttached;

  /// No description provided for @attachMedia.
  ///
  /// In en, this message translates to:
  /// **'ATTACH MEDIA'**
  String get attachMedia;

  /// No description provided for @groupLinkOptional.
  ///
  /// In en, this message translates to:
  /// **'Group Link (Optional Join)'**
  String get groupLinkOptional;

  /// No description provided for @minDelay.
  ///
  /// In en, this message translates to:
  /// **'Min Delay (sec)'**
  String get minDelay;

  /// No description provided for @maxDelay.
  ///
  /// In en, this message translates to:
  /// **'Max Delay (sec)'**
  String get maxDelay;

  /// No description provided for @launchCampaign.
  ///
  /// In en, this message translates to:
  /// **'LAUNCH CAMPAIGN'**
  String get launchCampaign;

  /// No description provided for @executingCampaign.
  ///
  /// In en, this message translates to:
  /// **'EXECUTING CAMPAIGN'**
  String get executingCampaign;

  /// No description provided for @operationComplete.
  ///
  /// In en, this message translates to:
  /// **'OPERATION COMPLETE'**
  String get operationComplete;

  /// No description provided for @dataGrabber.
  ///
  /// In en, this message translates to:
  /// **'Members Grabber'**
  String get dataGrabber;

  /// No description provided for @extractMemberDesc.
  ///
  /// In en, this message translates to:
  /// **'Extract all active members from any WhatsApp group you belong to.'**
  String get extractMemberDesc;

  /// No description provided for @targetGroups.
  ///
  /// In en, this message translates to:
  /// **'TARGET GROUPS'**
  String get targetGroups;

  /// No description provided for @membersStream.
  ///
  /// In en, this message translates to:
  /// **'MEMBERS STREAM'**
  String get membersStream;

  /// No description provided for @noDataStreaming.
  ///
  /// In en, this message translates to:
  /// **'No data streaming yet.'**
  String get noDataStreaming;

  /// No description provided for @numberValidator.
  ///
  /// In en, this message translates to:
  /// **'Number Filter'**
  String get numberValidator;

  /// No description provided for @numberValidatorDesc.
  ///
  /// In en, this message translates to:
  /// **'Verify phone numbers and filter out corrupt or non-whatsapp accounts.'**
  String get numberValidatorDesc;

  /// No description provided for @readyForScanning.
  ///
  /// In en, this message translates to:
  /// **'READY FOR SCANNING'**
  String get readyForScanning;

  /// No description provided for @scanResults.
  ///
  /// In en, this message translates to:
  /// **'SCAN RESULTS'**
  String get scanResults;

  /// No description provided for @totalScanned.
  ///
  /// In en, this message translates to:
  /// **'TOTAL SCANNED'**
  String get totalScanned;

  /// No description provided for @validAccounts.
  ///
  /// In en, this message translates to:
  /// **'VALID ACCOUNTS'**
  String get validAccounts;

  /// No description provided for @corruptMissing.
  ///
  /// In en, this message translates to:
  /// **'CORRUPT/MISSING'**
  String get corruptMissing;

  /// No description provided for @accountWarmer.
  ///
  /// In en, this message translates to:
  /// **'Account Warmer'**
  String get accountWarmer;

  /// No description provided for @accountWarmerDesc.
  ///
  /// In en, this message translates to:
  /// **'Simulate natural conversation between two accounts to build trust.'**
  String get accountWarmerDesc;

  /// No description provided for @phoneJid1.
  ///
  /// In en, this message translates to:
  /// **'PHONE JID 1'**
  String get phoneJid1;

  /// No description provided for @phoneJid2.
  ///
  /// In en, this message translates to:
  /// **'PHONE JID 2'**
  String get phoneJid2;

  /// No description provided for @totalMessages.
  ///
  /// In en, this message translates to:
  /// **'TOTAL MESSAGES'**
  String get totalMessages;

  /// No description provided for @averageDelay.
  ///
  /// In en, this message translates to:
  /// **'AVG DELAY (SEC)'**
  String get averageDelay;

  /// No description provided for @terminateWarming.
  ///
  /// In en, this message translates to:
  /// **'TERMINATE WARMING'**
  String get terminateWarming;

  /// No description provided for @startWarming.
  ///
  /// In en, this message translates to:
  /// **'START WARMING'**
  String get startWarming;

  /// No description provided for @warmingTelemetry.
  ///
  /// In en, this message translates to:
  /// **'WARMING TELEMETRY'**
  String get warmingTelemetry;

  /// No description provided for @noActivity.
  ///
  /// In en, this message translates to:
  /// **'No activity yet.'**
  String get noActivity;

  /// No description provided for @systemThemeMode.
  ///
  /// In en, this message translates to:
  /// **'System Theme Mode'**
  String get systemThemeMode;

  /// No description provided for @cyberpunkSFX.
  ///
  /// In en, this message translates to:
  /// **'Cyberpunk SFX'**
  String get cyberpunkSFX;

  /// No description provided for @enableSFX.
  ///
  /// In en, this message translates to:
  /// **'Enable Sound Effects'**
  String get enableSFX;

  /// No description provided for @languageIntegration.
  ///
  /// In en, this message translates to:
  /// **'Language Integration'**
  String get languageIntegration;

  /// No description provided for @switchLanguage.
  ///
  /// In en, this message translates to:
  /// **'Switch to {lang}'**
  String switchLanguage(String lang);

  /// No description provided for @connectivityNode.
  ///
  /// In en, this message translates to:
  /// **'CONNECTIVITY NODE'**
  String get connectivityNode;

  /// No description provided for @evolutionApiHost.
  ///
  /// In en, this message translates to:
  /// **'Evolution API Host'**
  String get evolutionApiHost;

  /// No description provided for @globalMasterKey.
  ///
  /// In en, this message translates to:
  /// **'Global Master Key'**
  String get globalMasterKey;

  /// No description provided for @nodeHealthStatus.
  ///
  /// In en, this message translates to:
  /// **'Node Health Status'**
  String get nodeHealthStatus;

  /// No description provided for @pingServer.
  ///
  /// In en, this message translates to:
  /// **'PING SERVER'**
  String get pingServer;

  /// No description provided for @safetyProtocols.
  ///
  /// In en, this message translates to:
  /// **'SAFETY PROTOCOLS'**
  String get safetyProtocols;

  /// No description provided for @messageBatchDelay.
  ///
  /// In en, this message translates to:
  /// **'Delay: {min}s - {max}s'**
  String messageBatchDelay(int min, int max);

  /// No description provided for @dailyTransmissionLimit.
  ///
  /// In en, this message translates to:
  /// **'Daily Transmission Limit'**
  String get dailyTransmissionLimit;

  /// No description provided for @aiPersonaEngine.
  ///
  /// In en, this message translates to:
  /// **'AI PERSONA ENGINE'**
  String get aiPersonaEngine;

  /// No description provided for @coreModel.
  ///
  /// In en, this message translates to:
  /// **'Core Reasoning Model'**
  String get coreModel;

  /// No description provided for @creativityThreshold.
  ///
  /// In en, this message translates to:
  /// **'Creativity Threshold'**
  String get creativityThreshold;

  /// No description provided for @osVersion.
  ///
  /// In en, this message translates to:
  /// **'OS VERSION'**
  String get osVersion;

  /// No description provided for @navGrabber.
  ///
  /// In en, this message translates to:
  /// **'Members Grabber'**
  String get navGrabber;

  /// No description provided for @navLinks.
  ///
  /// In en, this message translates to:
  /// **'Links Grabber'**
  String get navLinks;

  /// No description provided for @swapLanguageToast.
  ///
  /// In en, this message translates to:
  /// **'System Language: {locale}'**
  String swapLanguageToast(String locale);

  /// No description provided for @systemLogs.
  ///
  /// In en, this message translates to:
  /// **'SYSTEM LOGS'**
  String get systemLogs;

  /// No description provided for @awaitingCommands.
  ///
  /// In en, this message translates to:
  /// **'Awaiting Commands...'**
  String get awaitingCommands;

  /// No description provided for @groupSenderTitle.
  ///
  /// In en, this message translates to:
  /// **'Group Sender'**
  String get groupSenderTitle;

  /// No description provided for @startSending.
  ///
  /// In en, this message translates to:
  /// **'START SENDING'**
  String get startSending;

  /// No description provided for @logs.
  ///
  /// In en, this message translates to:
  /// **'LOGS'**
  String get logs;

  /// No description provided for @typeMessage.
  ///
  /// In en, this message translates to:
  /// **'Type Message...'**
  String get typeMessage;

  /// No description provided for @engineSettings.
  ///
  /// In en, this message translates to:
  /// **'ENGINE SETTINGS'**
  String get engineSettings;

  /// No description provided for @running.
  ///
  /// In en, this message translates to:
  /// **'RUNNING'**
  String get running;

  /// No description provided for @connection.
  ///
  /// In en, this message translates to:
  /// **'Connection'**
  String get connection;

  /// No description provided for @googleMaps.
  ///
  /// In en, this message translates to:
  /// **'Google Maps'**
  String get googleMaps;

  /// No description provided for @crmDashboard.
  ///
  /// In en, this message translates to:
  /// **'CRM Dashboard'**
  String get crmDashboard;

  /// No description provided for @opportunityHunter.
  ///
  /// In en, this message translates to:
  /// **'Opportunity Hunter'**
  String get opportunityHunter;

  /// No description provided for @businessSettings.
  ///
  /// In en, this message translates to:
  /// **'Business Settings'**
  String get businessSettings;

  /// No description provided for @aiAssistant.
  ///
  /// In en, this message translates to:
  /// **'AI Assistant'**
  String get aiAssistant;

  /// No description provided for @cloudServer.
  ///
  /// In en, this message translates to:
  /// **'Cloud Server'**
  String get cloudServer;

  /// No description provided for @themeSettings.
  ///
  /// In en, this message translates to:
  /// **'Theme Settings'**
  String get themeSettings;

  /// No description provided for @membersGrabber.
  ///
  /// In en, this message translates to:
  /// **'Members Grabber'**
  String get membersGrabber;

  /// No description provided for @linksGrabber.
  ///
  /// In en, this message translates to:
  /// **'Links Grabber'**
  String get linksGrabber;

  /// No description provided for @numberFilter.
  ///
  /// In en, this message translates to:
  /// **'Number Filter'**
  String get numberFilter;

  /// No description provided for @import.
  ///
  /// In en, this message translates to:
  /// **'Import'**
  String get import;

  /// No description provided for @fileUpload.
  ///
  /// In en, this message translates to:
  /// **'File Upload'**
  String get fileUpload;

  /// No description provided for @campaignContent.
  ///
  /// In en, this message translates to:
  /// **'Campaign Content'**
  String get campaignContent;

  /// No description provided for @groupLink.
  ///
  /// In en, this message translates to:
  /// **'Group Link'**
  String get groupLink;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
