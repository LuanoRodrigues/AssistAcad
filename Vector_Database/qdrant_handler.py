import hashlib
import json
from typing import List, Dict, Optional
import re
from collections import defaultdict
import logging
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.grpc import SparseVectorParams, Modifier
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import VectorParams, SparseVectorParams, Distance, Modifier
from Pychat_module.gpt_api import call_openai_api
import uuid
from File_management.exporting_files import export_results
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from yellowbrick.cluster import KElbowVisualizer
from kneed import KneeLocator
import matplotlib.pyplot as plt
result_api ={'overarching_theme': 'Evaluating Cyber Operation Attribution', 'structure': ['{"heading":"Evaluating Cyber Operation Attribution","paragraphs":["Expert assessments could significantly enhance the evaluation of evidence in the context of cyber operation attribution. In cases where the International Court of Justice (ICJ) is involved, the appointment of experts to examine and interpret evidence could provide an objective framework for assessment. This mirrors the historical precedent set during the Corfu Channel case, where experts played a pivotal role in determining the facts surrounding the incident. Their objective evaluations would assist in weighing the evidence and eliminating alternative possibilities, ultimately aiding in the attribution to the accused State. However, the inherent challenges of collecting evidence in cyber operations—especially those executed discreetly through proxies—cannot be overstated, making the attribution process complex and fraught with difficulties. Therefore, exploring the applicability of the due diligence principle in this context emerges as a critical consideration for establishing state responsibility in cyber operations (Mikanagi, 2021, p. 1030).","The high evidentiary thresholds required for proving cyber-attacks present significant hurdles for victim states seeking redress. One pressing question is how any victim-state can substantiate claims that a perpetrator state has committed an international wrong in the cyber domain, particularly given the myriad challenges related to concealment and the complexities of digital evidence. The obscured nature of cyber operations often makes it difficult for states to gather concrete evidence that meets the high standards of proof typically expected in international law. This situation leaves victim states in a precarious position, as they struggle to navigate the intricacies of attribution while facing the daunting task of overcoming these evidentiary barriers (Aravindakshan, 2021, p. 291).","Attribution of cyber operations not only requires technical expertise but also involves navigating a maze of legal and policy questions concerning government responsibility. The technical challenges associated with pinpointing the source of a cyber-attack are just the beginning; they give rise to broader legal and policy implications regarding when and how states can be held accountable for such actions. The contested nature of these issues illustrates the complexity of establishing clear standards for attribution in the cyber realm. As cyber threats continue to evolve, the need for a robust legal framework that addresses these challenges becomes increasingly urgent, necessitating a concerted effort among states to clarify the rules governing state responsibility in cyberspace (Eichensehr, 2020, p. 520).","In response to the difficulties surrounding cyber-attack attribution, researchers have proposed the establishment of a due diligence framework aimed at setting minimum standards. This framework posits that a due diligence failure occurs when a state is aware of a cyber operation being conducted from its territory that violates the rights of another state but neglects to take reasonable preventive measures. Although the concept of due diligence lacks a clear definition in law, it has been reflected in significant judicial decisions, such as the ICJ\'s Corfu Channel Judgment. This ruling underlined the obligation of states to prevent their territories from being used for actions that infringe upon the rights of others. With the rising tide of cyber-attacks and the insufficient development of international law in this area, there is a pressing need for states to engage actively in establishing norms and standards for attribution (Chircop, 2018; Greiman, 2021, p. 107).","The current landscape of international cybersecurity law is at a pivotal juncture, exacerbated by the increasing frequency of cyber-attacks and the apparent lack of coherent responses from states. The absence of a unified approach to addressing cyber operations has resulted in a power vacuum, which has, in turn, fostered non-state norm-making initiatives. As highlighted by various scholars, this situation presents a unique opportunity for the international community to leverage existing initiatives to develop standards and norms regarding cyber-attack attribution. By fostering collaborative efforts among states and stakeholders, it is possible to create a more robust framework that can effectively address the complexities of cyber operations and enhance accountability in the digital age (Mačák, 2017; Greiman, 2021, p. 107)."]}', '{"heading":"Legal Challenges in Cybersecurity","paragraphs":["Current legal frameworks significantly hinder states\' ability to exercise self-defense in response to cyber attacks. As noted by Finlay and Payne (2019), the conventional principles surrounding self-defense and attribution are inadequate for addressing the complexities of cyber armed attacks. The inherent technical challenges associated with accurately attributing cyber incidents complicate the legal requirements for states seeking to justify a self-defense response. This inadequacy effectively constrains states from exercising their right to self-defense, thereby exacerbating the vulnerability of nations facing aggressive cyber operations.","The admissibility of evidence obtained through wrongful acts presents another layer of complexity within the legal frameworks governing cybersecurity. According to Roscini (2015), the International Court of Justice (ICJ) does not have explicit rules barring the use of such evidence, which can be crucial in inter-state disputes. This is particularly pertinent in instances where espionage or cyber exploitation may be deemed internationally wrongful acts. The ICJ\'s historical reliance on evidence obtained through questionable means, as illustrated in the Corfu Channel case, suggests that circumstantial evidence may carry significant probative weight even if it stems from illicit activities.","Moreover, the ICJ\'s approach reflects a broader understanding of evidence collection in the context of state sovereignty. Unlike domestic legal systems, where the protection of defendants\' rights is paramount, inter-state litigation operates under principles of sovereign equality, as highlighted by Thirlway. This context allows for the consideration of evidence that might be inadmissible in domestic courts, underscoring the unique challenges that arise in cyber contexts. Thus, the admissibility of evidence remains a critical concern for states attempting to navigate the complex interplay of legality and cybersecurity.","In addition to the challenges of evidence admissibility, other international tribunals have increasingly enforced compliance with evidence requests despite claims of national security. Ronen (2020) points out that some tribunals have shown less deference to state positions, demanding sensitive information that states have complied with under scrutiny. This precedent highlights the evolving landscape of international law in relation to cybersecurity, where the balance between national security and accountability is continually tested.","Lastly, the architecture of the Internet poses significant hurdles to states\' responses to cyber threats, particularly regarding sovereignty issues. Banks (2016) emphasizes that the traditional Westphalian concept of sovereignty complicates the establishment of effective norms for managing below-threshold conflicts in cyberspace. This is especially critical when dealing with non-state actors, such as transnational terrorist groups deploying malware across borders. The lack of state consent for cyber operations can render responses unlawful, illustrating the need for a reevaluation of international legal frameworks to better address the realities of cyberspace and enhance states\' capabilities to defend against cyber threats."]}', '{"heading":"Emerging Norms and Standards","paragraphs":["The development of new customary norms in cyberspace is further facilitated by the uniqueness of the domain. The distinct characteristics of cyberspace create an environment where traditional norms can evolve rapidly. As the applicability of international law to cyber operations becomes increasingly accepted, the pressing need to address emerging technologies fosters the swift creation of customary law. This phenomenon is akin to the instantaneous establishment of principles regarding sovereignty in outer space following the launch of the first satellites. Consequently, a due diligence standard for attribution in cyberspace may emerge swiftly, particularly if state practices begin to reflect a cohesive approach towards attributing responsibility for cyber incidents (Chircop, 2018, p. 668).","The call for establishing an independent body for cyber attribution is gaining traction, as it could significantly enhance the credibility of evidence in cyber operation cases. The existing ambiguity surrounding international procedural law complicates the situation, particularly regarding standards of proof and the admissibility of various types of evidence. Even when cases are presented before international courts, the lack of clarity can hinder effective legal resolution. Notably, the International Court of Justice (ICJ) jurisprudence indicates that indirect and circumstantial evidence may be utilized when direct evidence is absent, especially if cooperation from the state involved is lacking. The possibility of lowering the required standard of proof in less severe cases could further facilitate the establishment of responsibility in cyber incidents (Mikanagi e Macak, 2020, p. 22).","However, shifting the burden of proof to the accused state poses significant challenges and may not be the optimal solution. Some scholars have suggested that the burden should rest with the perpetrator state to demonstrate its non-involvement in any cyberattacks. Despite such proposals, this approach has been met with skepticism, as it could unfairly impose excessive responsibility on the respondent states. Historical precedents indicate that courts have previously rejected this shift, suggesting that a more balanced approach is necessary. A viable alternative would be to lower the evidentiary standard to \'clear and convincing,\' even when direct evidence is lacking. This adjustment could allow for a more equitable determination of responsibility within the context of international law (Brunner et al., 2019, p. 107).","The establishment of clearer norms and standards surrounding cyber attribution is crucial in fostering greater accountability among state actors. As emerging customary norms take shape, it is essential for states to adopt a proactive stance in acknowledging their cyber actions and responsibilities. This shift towards greater transparency could lead to a more predictable and stable cybersecurity environment, where states are less likely to engage in malicious activities under the veil of anonymity. Moreover, a collective acknowledgment of norms can encourage cooperation among nations in combating cyber threats, thereby enhancing global cybersecurity resilience (Chircop, 2018, p. 668).","In conclusion, the evolving landscape of cyberspace necessitates the rapid development of customary norms and standards for attribution. The establishment of an independent body for cyber attribution, along with a shift towards lower evidentiary standards, could significantly improve the accountability of states involved in cyber operations. As states navigate this complex domain, fostering a culture of responsibility and transparency will be vital to ensuring that the international community can effectively respond to and deter cyber threats. As such, the interplay between emerging norms and the legal frameworks governing cyber operations will play a critical role in shaping the future of international cybersecurity (Mikanagi e Macak, 2020, p. 22; Brunner et al., 2019, p. 107)."]}', '{"heading":"Evidence Credibility and Compliance","paragraphs":["The bibliography includes significant works on cyber attribution and law, highlighting the complexity of establishing credible evidence in cyber operations. Augustine (2014) discusses the concept of neutrality in cyber conflicts, emphasizing the need for a textual analysis of traditional Just In Bello rules as they apply to cyber warfare. This foundational work sets the stage for understanding how legal frameworks must adapt to the evolving landscape of cyber operations, where the attribution of malicious actions is often obscured by technological advances and the anonymity of the internet.","Clark and Landau (2010) further the discourse by addressing the challenges of attribution in the context of cyberattacks. They propose strategies to inform U.S. policy on deterring cyber threats, underscoring that effective attribution is crucial not only for legal compliance but also for crafting appropriate responses to cyber incidents. Their insights reveal that without credible evidence, states may struggle to respond decisively, potentially leading to a cycle of impunity for cyber aggressors.","The discussion on thresholds of \'use of force\' and \'armed attack\' in cyber conflict is notably advanced by Dev (2015). This work highlights the definitional gaps that exist in international law concerning cyber operations, advocating for a formal U.N. response framework. By addressing these gaps, Dev emphasizes the importance of credible evidence in determining when a cyber incident escalates to a level warranting international legal action, thus reinforcing the need for compliance with established legal norms.","Faga (2017) further analyzes the implications of transnational cyber threats through the lens of international humanitarian law. By distinguishing between cybercrime, cyber attacks, and cyber warfare, this work underscores the necessity of precise and credible evidence to classify cyber operations correctly. The implications of these classifications are significant, as they dictate the legal responses available to states facing cyber threats and highlight the need for rigorous evidence-gathering processes.","Lastly, Guitton (2015) contributes to the understanding of attribution by proposing a comprehensive framework for cybersecurity strategies in the face of cyber warfare. This framework emphasizes the importance of credibility and compliance in evidence gathering, as well as the need for international cooperation in attributing cyber incidents. The collective works cited, including those from Lin (2016) and Schmitt (2017), illustrate a growing consensus on the critical role that credible evidence plays in ensuring accountability and upholding the rule of law in cyberspace."]}']}
to_be_replaced={"overarching_theme":"Legal and Ethical Challenges in Cyber Attribution","structure":[{"heading":"h1","title":"Cyber Attribution: Challenges and Frameworks","paragraph_ids":["67bc2e0e","5209f718","843fb02f","f85968ef"]},{"heading":"h2","title":"Expert Assessments and Legal Frameworks","paragraph_ids":["67bc2e0e","5209f718","4ad2686d"]},{"heading":"h3","title":"Assessing Evidence and Legal Barriers","paragraph_ids":["250b1dfd","40116d22","0c8ef2f2"]},{"heading":"h2","title":"Emerging Norms and Due Diligence in Cyberspace","paragraph_ids":["843fb02f","05963d0d","082366c0"]},{"heading":"h2","title":"International Compliance and Evidence Requests","paragraph_ids":["7f0669ad"]},{"heading":"h2","title":"Sovereignty and Cyber Threats","paragraph_ids":["d7f89fa3"]}]}
clusters_to_test ={0: [{'id': '67bc2e0e', 'content': ('  Expert assessments could aid in evaluating evidence for cyber operation attribution.', '“If a case concerning the attribution of cyber operations is brought before the ICJ, the Court can appoint experts to examine the evidence, as it did in the Corfu Channel case.45 The experts’ objective assessment would help evaluate the weight of evidence in eliminating possibilities other than the attribution to the accused State. However, considering the technical challenge involved in collecting evidence relating to the attribution of cyber operations to States that discreetly conduct these operations through proxies, the difficulty of attributing cyber operations to States cannot be underestimated. Therefore, as an alternative path to State responsibility, the applicability of the due diligence principle to cyber operations deserves careful but serious consideration.” (Mikanagi, 2021, p. 1030)')}, {'id': '5209f718', 'content': ("Current legal frameworks hinder states' self-defense in cyber attacks.", '“The conventional principles of self-defense and attribution are poorly suited to dealing with cyber armed attacks. The technical problems of attribution in cyberspace may make it practically impossible for victim states to meet the legal requirements of both attribution and self-defense. Under the current legal framework, states are effectively prevented from utilizing the right to self-defense in response to a cyber armed attack.” (Finlay e Payne, 2019, p. 206)')}, {'id': '843fb02f', 'content': ('Emerging Customary Norms in Cyberspace May Accelerate Due to Unique Characteristics', '“The development of new customary norms in cyberspace is further facilitated by the uniqueness of the domain. While the applicability of international law to the cyber context is now settled, the urgency of coping with new technologies enables customary law to come into existence very rapidly.201 In the same way that novel principles concerning sovereignty in outer space developed ‘instantly’ after the first satellites were launched,202 a due diligence standard of attribution might quickly develop with respect to cyberspace. On balance, instances of supportive State practice lack the quantum and uniformity to establish a crystallized or emerging customary norm. If, however, the United States’ response to the Sony and DNC hacks signals a newfound willingness to allege State responsibility following cyber operations, a due diligence standards of attribution might soon follow.” (Chircop, 2018, p. 668)')}, {'id': 'f85968ef', 'content': ('The bibliography includes significant works on cyber attribution and law.', 'Augustine, Zachary P. “Cyber Neutrality: A Textual Analysis of Traditional Just In Bello Neutrality Rules Through A Purpose-Based Lens.” The Air Force Law Review 71 (2014): 69–106. \xa0Clark, David D. and Susan Landau. “Untangling Attribution.” In Proceedings of a Workshop on Deterring Cyberattacks: Informing Strategies and Developing Options for US Policy, 25–40. Washington D.C.: National Academies Press, 2010. https://www.nap.edu/read/12997/chapter/4. \xa0Dev, Priyanka R. “’Use of Force’ and ‘Armed Attack’ Thresholds in Cyber Conflict: The Looming Definitional Gaps and the Growing Need for Formal U. N. Response.” Texas International Law Journal 50, no. 2/3, (Spring/ Summer 2015): 381–401. https://texashistory.unt.edu/. Faga, Hemen Philip. “The Implications of Transnational Cyber Threats in International Humanitarian Law: Analyzing the Distinction Between Cybercrime, Cyber Attack, and Cyber Warfare in the 21st Century.” Baltic Journal of Law & Politics 10, no.1 (2017): 1–34. https://www.degruyter.com/. \xa0Guitton, Clement. “Attribution.” In Cybersecurity Policies and Strategies for Cyberwarfare Prevention, Richet, Jean-Loup, ed., 37–52. Hershey, PA: Information Science Reference, 2015. \xa0Joint Publication (JP) 3–12. Cyberspace Operations. 30 November 2011. https://www.doctrine.af.mil/. Lin, Herbert S. “Attribution of Malicious Cyber Incidents: From Soup to Nuts.” Journal of International Affairs 70, no. 1, (Winter 2016): 75–129. https://jia.sipa.columbia.edu/. Margulies, Peter. “Sovereignty and Cyber Attacks: Technology’s Challenge to the Law of State Responsibility.” Melbourne Journal of International Law 14, no. 2 (2013): 496–519. https://law.unimelb.edu.au/. \xa0Mejia, Eric. “Act and Actor Attribution in Cyberspace: A Proposed Analytic Framework.” Strategic Studies Quarterly 8, no. 1 (Spring 2014): 114–132. https://www.airuniversity.af.edu/. \xa0Mudrinich, Erik M. “Cyber 3.0: The Department of Defense Strategy for Operating in Cyberspace and the Attribution Problem.” The Air Force Law Review 68 (2012): 167–206. \xa0Rid, Thomas and Ben Buchanan. “Attributing Cyber Attacks.” Journal of Strategic Studies 38, no. 1–2 (2015): 4–37. doi:10.1080/01402390.2014.977382. Roscini, Marco. “Evidentiary Issues in International Disputes Related to State Responsibility for Cyber Operations.” Texas International Law Journal 50, no. 2/3, (Spring/Summer 2015): 233–273. https://westminsterresearch .westminster.ac.uk/. Schmitt, Michael N., ed. Tallinn Manual 2.0 on the International Law Applicable to Cyber Operations. Cambridge: Cambridge University Press, 2017. _____. “The Law of Cyber Targeting.” Naval War College Review 68, no. 2 (Spring 2015): 11–29. https://digital-commons.usnwc.edu/. \xa0Schmitt, Michael N. and Liis Vihul. “Proxy Wars in Cyberspace: The Evolving International Law of Attribution.” Fletcher Security Review 1, no. 2, (2014): 53–72. https://ccdcoe.org/. \xa0United States Judge Advocate General’s Legal Center and School. Law of Armed Conflict Deskbook. Charlottesville: VA, International and Operational Law Department, 2015. http://www.loc.gov/. United States. Department of Defense. Office of General Counsel. Department of Defense Law of War Manual. (May 2016): 985–1000. https://apps .dtic.mil/dtic/tr/fulltext/u2/1014128.pdf.')}, {'id': '250b1dfd', 'content': ('The admissibility of evidence obtained through wrongful acts is not explicitly barred by the ICJ, allowing for reliance on such evidence in certain cases.', 'Assuming, arguendo, that espionage and cyber exploitation are, at least in certain instances, internationally wrongful acts, what is the probative value of the evidence so collected? There is no express rule in the Statute of the ICJ providing that evidence obtained through a violation of international law is inadmissible. It is also not a general principle of law, as it seems to be a rule essentially confined to the US criminal system.258 As Thirlway argues, the rule in domestic legal systems is motivated by the need to protect the defendant against the wider powers of the prosecutor and its possible abuses: in inter-state litigation, there is no criminal trial and no dominant party, as the litigants are states in a position of sovereign equality.259 In the Corfu Channel case, the ICJ did not dismiss evidence illegally obtained by the United Kingdom in Operation Retail; on the contrary, it relied on it in order to determine the place of the accident and the nature of the mines.260 In fact, Albania never challenged the admissibility of the evidence acquired by the British Navy,261 and the Court did not address the question. What it found was not that the evidence had been illegally obtained, but that the purpose of gathering evidence did not exclude the illegality of certain conduct.262 In general, “the approach of the Court is to discourage self-help in the getting of evidence involving internationally illicit acts, not by seeking to impose any bar on the employment of evidence so collected, but by making it clear that such illicit activity is not necessary, since secondary evidence will be received and treated as convincing in appropriate circumstances.”262 In a cyber context, this means that the fact that direct evidence is located in the computers or networks of another state does not entitle the interested litigant to access them without authorization to submit it in the proceedings, but allows the Court to give more probative weight to circumstantial evidence.(Marco Roscini e Roscini, 2015, p. 19)')}, {'id': '40116d22', 'content': ('High evidentiary thresholds pose challenges for victim states to prove cyber-attacks.', '“Where does this leave cyber-attacks? Given these high evidentiary thresholds, how is any victim-state supposed to prove that the perpetrator state carried out an international wrong in cyberspace, with all its vagaries including concealment and disguising issues?” (Aravindakshan, 2021, p. 291)')}, {'id': '4ad2686d', 'content': ('Attribution involves challenging legal and policy questions regarding government responsibility.', '"The difficult technical side of attribution is just the precursor to highly contested legal and policy questions about when and how to accuse governments of responsibility for cyberattacks." (Eichensehr, 2020, p. 520)')}, {'id': '0c8ef2f2', 'content': ('Establishing an independent body for cyber attribution could improve evidence credibility.', '“The apparent stringency of the substantive standards is exacerbated by the lack of clarity of the applicable international procedural law. Even if a case was brought before one of the international tribunals, the relevant rules concerning the applicable standard of proof and the admissibility of indirect or circumstantial evidence are unsettled and ambiguous. However, the jurisprudence of the ICJ indicates that indirect and circumstantial evidence can be relied upon if direct evidence is not available due to the lack of cooperation from the territorial State and the required standard of proof can be lowered in the cases of lesser gravity (section 4).” (Mikanagi e Macak, 2020, p. 22)')}, {'id': '7f0669ad', 'content': ('Other tribunals have enforced compliance with evidence requests despite national security claims.', '“Other tribunals have been less deferential to states’ positions and have requested information that was sensitive and confidential, and respondent states have complied with the requests, with the documents examined in camera. In Cyprus v Turkey the requested state refused to comply with the request, the EComHR reported it to the competent political body.180” (Ronen, 2020, p. 29)')}, {'id': 'd7f89fa3', 'content': ('The architecture of the Internet and sovereignty issues hinder responses to cyber threats from both state and nonstate actors.', '“Given the architecture of the Internet, the traditional Westphalian stance on sovereignty embedded in customary law and reflected by the IGE in Tallinn 2.0 may frustrate the development of workable norms for controlling below-threshold conflict in cyberspace.157 Consider the simple example of a nonstate, transnational terrorist group spreading malware across several States. Although many States are equipped to disrupt botnets or malware impacts through straightforward, technical cyber operations, the sovereignty rule could stand in the way of State responses to the terrorists that cross national borders. Absent State consent, any cyber operation in response to this kind of intrusion that constitutes a prohibited intervention is unlawful. The barrier applies to responses to States and to nonstate actors.158” (Banks, 2016, p. 1513)')}, {'id': '05963d0d', 'content': ('A due diligence framework is proposed to establish minimum standards for cyber-attack attribution.', '“Researchers have proposed a due diligence framework or minimal standards for attribution of cyber-attacks (Chircop, 2018). A due diligence failure occurs when a state has knowledge of a cyber operation being carried out from within its territory, contrary to the rights of another, and fails to take reasonable measures to prevent it (Tallinn, Rule 6 at 42). Though due diligence is not clearly defined in the law it was reflected by the International Court of Justice (ICJ) in its Corfu Channel Judgment: “It is every State’s obligation not to allow knowingly its territory to be used for acts contrary to the rights of other states (Corfu, 1949) and has been set forth as an obligation of States in the pronouncements of the International Law Association (ILA, 2014). With the rise of cyber-attacks globally and no end in sight, international cyber security law is at a critical juncture. The failure of states to engage in the development and applications of international law has left a power vacuum allowing for the emergence of non-state norm-making initiatives (Mačák, 2017). As suggested here there is an opportunity now to employ the many initiatives and proposals for the development of standards and norms and to engage the international community in attribution norm and standards building practices.” (Greiman, 2021, p. 107)')}, {'id': '082366c0', 'content': ('Shifting the burden of proof could be inadequate, and lower standards may enhance justice.', '“Thus, scholars have proposed to shift the burden of proof to the perpetrator state, which now has to prove that it had not been involved in a cyberattack. This seems to be an unsatisfying solution: Not only did the Court itself refuse such an approach in the past; a shift would also put too much responsibility on the respondent state. Therefore, a more plausible approach would be to lower the evidentiary standard to clear and convincing, even in cases where direct proof is missing. Additionally, the present authors have pointed out how the inability of the parties to produce sufficient evidence can be overcome through the usage of the Court’s power to appoint experts. This makes it possible to meet the clear and convincing standard and thus establish international responsibility.” (Brunner et al., 2019, p. 107)')}], 1: [{'id': '9a986de0', 'content': ("Lloyd's of London's insurance model may rely on political attributions of cyber actions.", '“This, however, is what Lloyd\'s of London attempts to achieve with its new insurance policy. In particular, Lloyd\'s of London is trying to link a State\'s political attribution statement, which States regularly stress is not a legal attribution in itself, to its own legal obligation to discharge proof that a cyber operation is "State-backed," thus excluding coverage for such an attack. Lloyd\'s of London\'s model clauses-as a preliminary step-only require that a State has attributed the incident itself, without providing any additional requirements as to evidentiary standards or rules. This would enable insurers to exclude insurance on the basis of insufficiently proven "political attribution" statements. If accepted by a court, such conclusions would rely on complete trust in a government\'s attribution assessment without any measure of oversight or transparency.” (Brunner, 2022, p. 190)')}, {'id': '8c497488', 'content': ('  Insufficient state practice hinders the establishment of customary norms for evidence in attributions.', '“Currently, there is insufficient state practice and a lack of opinio juris when it comes to standards of evidence in political attributions.43 For this reason, it is necessary to evaluate what should change in state practice. Regarding the first requirement (i.e. consistent and general state practice), it is noteworthy that states already tend to provide some level of evidence in attributions, as previously described.44 However, even though some level of state practice can be identified, the current practice cannot be considered consistent and general. Thus, this needs to be further developed. For instance, states could agree that all future public attributions will be substantiated by sufficient evidence to enable corroboration and crosschecking. This would lead to a more consistent and general practice, which would then be expected from states making public attributions going forward.” (Blauth e Gstrein, 2021, p. 9)')}, {'id': 'df967f28', 'content': ('Countermeasures may require high or intermediate proof standards.', '“For the taking of countermeasures, either a high or an intermediate standard of proof, i.e., either convincing evidence or preponderance of the evidence may apply.” (Dederer e Singer, 2019, p. 465)')}, {'id': '21da68c8', 'content': ('Public attribution creates domestic pressure for action against aggressors.', '“As it stands today, the evidentiary standard for public attribution outside the confines of established legal or other adjudicatory frameworks is context dependent and fundamentally political. The identity of the claimant bears directly on the credibility of its claim, with none of the formal evidentiary and other substantive and procedural safeguards available in most municipal legal settings to protect the integrity of evidence and witness testimony with the goal of allowing the facts and evidence to speak for themselves. Similarly, nation-states and other actors will often evaluate evidence with an eye toward what the consequences might be if the evidence were true. They are not neutral factfinders.” (Grotto, 2020, p. 9)')}], 2: [{'id': '5424ae91', 'content': ('Public pressure can force leaders to respond quickly despite lack of information.', '“In other cases, policymakers may have an attribution of a malicious cyber incident in hand (indeed, perhaps a high-confidence attribution) and choose not to make it public. One obvious reason for not “going public” is the reality that a public attribution will generate demands for public evidence, a point discussed earlier. But another reason for not “going public” is that the relationships between many nations that act against each other in cyberspace are complex and multidimensional. “Going public” may result in demands to take retaliatory action that, in the view of senior policymakers, may be unwise given the range of interests at stake. The consequences of any retaliatory action (i.e., the significance of a possible adversary response) must be taken into account, and before policymakers decide to retaliate, they must be willing to face the consequences of any such action.” (Lin, 2016, p. 125)')}, {'id': 'daf26c9e', 'content': ('shifting can counter cyber aggression.', '“Publicly attributing malicious cyber activity to a state in a timely manner and holding that state responsible through a burden-shifting model is likely to cause some backlash against the United States. However, actions taken in cyberspace that do not neatly fit into a recognized area of international law are bound to create ambiguity and “unease. As states continue to develop norms in cyberspace, the United States should harken back to the proverb by Thucydides: “The strong do what they can, and the weak suffer what they must.”107 The United States should not be constrained by inapplicable and unresponsive international legal regimes. Rather, the United States should confront cyber adversaries through a policy of rapid attribution and coercive diplomacy to deter future aggression, thereby building international law and norms that support the interests of the United States.” (Anderson, 2021, p. 67)')}, {'id': '9e40e4ff', 'content': ('Public attributions without consequences can damage reputations and promote irresponsible accusations.', '“Lastly, what if the accusing state makes a public attribution that later proves to be wrong, but it did not take concrete measures originally? Although the accused state does not suffer from the responding measures, harm to its fame and reputation has still been inflicted. Under such circumstances, should the accusing state be held partially responsible for the false attribution (which might have been intentional)? Would not holding it responsible encourage more ill-substantiated public accusations? This issue deserves more international discussion.” (Yang, 2022, p. 7)')}, {'id': '51c0f122', 'content': ('  Advanced cyber states are hesitant to share attribution information due to transparency concerns.', '“As the most advanced cyber states recognize the risks of cyber escalation, those states have good reason to become more transparent about attribution in service of the mutual restraint that could be gained by sharing attribution information. But to date, state concerns about revealing intelligence sources and methods counsel against transparency.48” (Banks, 2019, p. 196)')}], 3: [{'id': 'b5d368dd', 'content': ('Law enforcement efforts against foreign cyber crime must be ongoing and persistent.', '“This article has pointed to the value of criminal charges for both disrupting state-backed hacking and contributing to broader international efforts to respond to malicious state activity in cyberspace. But it would be a mistake to believe that criminal charges can stop foreign cyber crime. Instead, a better frame for thinking about the role of law enforcement is to compare it to law enforcement efforts against organized crime - constant efforts to reduce adversary gains and bring them to justice when possible. This persistent law enforcement will be a continuous response to nation states that increasingly turn to hacking to work against U.S. interests.” (Hinck and Maurer, 2019, p. 31)')}, {'id': 'd46a3eca', 'content': ('  Increased punishment severity alone may not deter online crime; social stigma and community shame play significant roles.', '“Moving beyond the mere perception of punishment to the actual punishment, many studies have found that increasing the severity of a punishment does not act as an effective deterring factor, especially due to the limited knowledge of the potential offenders of the law (Assembly Committee on Criminal Procedure (California), 1975, p. 78; Tonry & Farrington, 2005; William, Gibbs, & Erickson, 1980). But an increase of the severity of punishment can also be interpreted differently and in a wider meaning. John Braithwaite wrote in 1989 at the very beginning of an influential book that ‘societies with low crime rates are those that shame potently and judiciously; individuals who resort to crime are those insulated from shame over their wrongdoing’ (Braithwaite, 1989, p. 1). Braithwaite’s theory seeks to prevent crime not by deterrence, but by making more salient the feeling of shame for deviant behaviors. How can the state apply reintegrative shame theory for criminal behaviors on the Internet? The anonymity of the medium can prevent the offenders from a community to shame him for his actions. Hence, increasing attribution can result in a decrease of disinhibition (acting as psychological constraints upon crime), but only for individuals who already show strong communitarianism and interdependency. If his actions were to attack a technical device, there is limited evidence that hackers feel shame for their attacks (Turgeman-Goldschmidt, 2008). In many instances, they find new job opportunities as society recognizes and need their technical expertise to prevent further security breaches. The case of Owen Thor Walker, aka AKILL is telling. In December 2007, the New Zealand police arrested him in his bedroom, then aged 17 years old. The New Zealand police arrested him as part of a larger police operation led by the US Federal Bureau of Investigation. They accused Walker of being the leader of a group of hackers that operated a large botnet, and who had swindled £12.5 million (McMahon & Johnson, 2007). Walker faced a 10-year jail sentence. The head of the police electronic crime centre described Walker as very bright and was impressed by Walker’s technical skills to write malicious codes that evaded the watch of most commonly used anti-virus software. A year and half later, Walker received his sentence. The court fined him to £5,500 for cost and damages, then discharged him so that he could work with the police to tackle online crime (Johnson, 2008). Paradoxically, society welcomed to some extent Walker’s actions. He cannot have felt shamed as a punishment reduction and a job offer praised him for his skills and knowledge, putting aside what he has done with them. Braithwaite writes that ‘shaming is needed when conscience fails’, but paradoxically, for shaming to be effective also requires the individual to consciously understand the deviancy of his actions. Reintegrating communitarianism and interdependency, for which online identification is not an absolute requisite for online community, is a remedy for the effectiveness of shaming, or the fear of it. A change of policy should not only address Internet behavior, but should also address very broadly the deeper and more complex societal problem of individualism. Braithwaite, especially as he takes family as the first social sphere for the application of reintegrative shaming, advocates education at an early stage for the conscience to be shaped in certain ethical ways.” (Guitton, 2012, p. 1034)')}, {'id': '6227ae40', 'content': ('Community-Policing as a Model for Civilian Support', '“Essentially, I am proposing a larger-scale analog of the law enforcement support programs used in community-policing.380 I think these programs provide a useful conceptual model for the type of effort we are considering both because of the way they are structured and because of the type of support they provide.” (Brenner, 2007, p. 92)')}, {'id': '7e78f545', 'content': ('International law allows nuanced responses to proxy cyber operations.', '“The critical point to grasp is that the international law governing response options is often permissive in terms of allowing responses, but at the same time, can be very nuanced and even unsettled. Thus, every situation merits granular analysis when deciding how to limit, stop, and deter hostile cyber operations by cyber proxies. Over time, state practice in dealing with proxy cyber operations combined with statements from states regarding how they interpret the relevant international law will yield greater clarity on the options available to defeat and deter hostile proxy cyber operations.” (Johnson e Schmitt, 2021, p. 30)')}, {'id': 'a4c3cde6', 'content': ('Growing support for collective countermeasures may influence international law.', '“The last segment was dedicated to collective countermeasures. The possibility of their implementation remains controversial, but in recent years there has been growing support for them both in academia and in state practice. Unless this trend changes, collective countermeasures may soon become a stable part of international law.” (Spáčil, 2023, p. 108)')}, {'id': '0a2c01e3', 'content': ('The OPM hack illustrates significant gaps in international law regarding cyber espionage.', 'The OPM hack, for example, may have severely undermined U.S. national security at a scale not seen previously. Yet, from the perspective of international law, the OPM hack was an act of espionage, which international law either fails to regulate or affirmatively permits. As such, it is not surprising to see accusations against China avoid condemnation for the OPM hack in international legal terms.107” (Banks, 2021, p. 1064)')}, {'id': 'f056529c', 'content': ("Giumelli's framework offers a nuanced perspective on sanction effectiveness relative to other foreign policy tools.", '“The analytical framework developed by Giumelli represents a nuanced approach to the assessment of sanction effectiveness in comparison with the mainstream assessment. Although changing the target’s behaviour can be among the sender’s objectives, it is not the only one. An estimation of the impact of sanctions through the lens of their goal(s) might provide a clearer understanding of the position of sanctions amid other foreign policy tools and their relative, as opposed to absolute, impact.” (Rusinova e Martynova, 2024, p. 172)')}, {'id': 'ecaccd20', 'content': ('The skill level of hackers influences the degree of national responsibility imposed.', '“The closer a victim state can get to proving an accused state’s involvement, the more severe the reputational consequences. Importantly, however, this does not mean that the reputational consequences are nil for evidence below this threshold. Similarly, even if sponsors are operating beyond the reach of the law, victims may have a variety of retaliatory means (such as sanctions, but also potentially cyber reprisals) at their disposal that are also capable of skirting legal prohibition in much the same way. Host states probably recognize this fact, and thus they should be expected to perceive little value added to delegation when either (a) private hackers are unsympathetic to state interests or (b) available sympathizers are too unsophisticated to achieve any worthwhile foreign policy aims. The exception is among states that can levy financial or ideological incentives but lack their own in-house cyber expertise. In this way, states with weak internal cyber capabilities might adopt mercenary methods.” (Canfil, 2016, p. 223)')}, {'id': '34a03414', 'content': ('Lack of plausible deniability may deter state sponsors from outsourcing operations.', '“Without plausible deniability, would-be sponsors face a variety of disincentives. In conventional spaces, some speculate that outsourcing generally leads to wider disruption and collateral damage [20], whereas state control minimizes these byproducts [112]. In the cyber context, host states may not wish to risk bringing neutral parties into the fray, accidentally damaging assets in blue space, or violating emerging norms of international humanitarian law, such as the prohibition on attacking critical infrastructure in peacetime. Mounting evidence has also led some researchers and policymakers to cautiously conclude that cyber conflict is not inherently escalatory, anyway [56, 58]. If true, why jeopardize operational efficiency by outsourcing to outside actors who might be less-than-reliable? In converse, command centralization may come with advantages in terms of the division of skilled labor, economies of scale, and operational coherence.” (Canfil, 2020, p. 33)')}], 4: [{'id': 'b73740c6', 'content': ("Sophisticated cyber attacks can be attributed to states using the 'overall control' standard.", '“Its merits can be demonstrated by considering a number of scenarios. The first concerns APT actors committing technically sophisticated attacks on a global scale; for instance, espionage, attacks on critical infrastructure systems or other high-end attacks. In order to design and execute such attacks, APTs need resources, time, technical knowledge, intelligence information, platforms and organisational capabilities. In other words, such operations require long-term investment and close coordination in order to be executed. Previously we said that the sophistication of the attack and of the APT actor can provide evidence of state involvement86 but the question to ask is how this can lead to attribution. It transpires that the ‘overall control’ indices of equipping, resourcing and planning can indeed provide the most probable description of the type of relationship between states and APTs that can support such action when institutional, functional or agency links are missing, and if the targets and goals of the operation are also taken into account. It follows that when the UK said that APT10 has an ‘enduring relationship with the Chinese Ministry of State Security and operates to meet Chinese State requirements’,87 the ‘overall control’ criterion could form the basis of attributing its malicious cyber activities to China. Equally, Stuxnet, one of the most sophisticated cyber attacks, can be attributed to the USA and/or Israel on that basis.” (Tsagourias e Farrell, 2020, p. 963)')}, {'id': 'cf82e79e', 'content': ('State-sponsored cyberwarriors possess significant technical capabilities but face a skilled adversary.', '“In any case, state-sponsored cyberwarriors certainly have the technical capacity to identify adversaries biometrically. As I mentioned above, modern intelligence agencies have enormous resources to draw upon, including various cyberweapons merchants and others who provide a cornucopia of communication and media interdiction tools, rootkits, remote session hijacking tools, worms, viruses, zero-day exploits, and sundry other tools to spy on cyberadversaries in situ. That said, the other side has comparable access to such tools and are aware that these tools can be used against them. Rooting a journalists’ computer is very different from rooting the computer of a highly skilled security specialist in the employ of a state sponsor. This is very much a case of cyber cat and mouse where neither has the predictably clear advantage. Could Western intelligence agencies root computers of state adversaries? Sure, but it’s not very likely unless the target has a rookie asleep at the console.” (Berghel, 2017, p. 87)')}, {'id': '90209f55', 'content': ('The Article discusses the challenges of cyber-attribution and proposes a model linking it to state responses.', '“This Article has outlined some of the major legal issues in relation to cyber-attacks, focusing particularly on the question of attribution. The novel characteristics of cyber-attacks make the existing standards of proof and degrees of control required to establish attribution extremely difficult to determine. As a result, attribution is regarded by many scholars as one of the most significant and immediate practical obstacles to resolving the legal uncertainty surrounding this emerging issue.249 This Article has analyzed the different approaches to cyber-attribution and proposed a model whereby attribution requirements are linked with the state’s response to a cyber-incident. This approach leverages existing international law, discourages states from pursuing retaliatory responses, and incentivizes host states to assist the victims of cyber-attack in identifying the perpetrators. Issues remain regarding compulsory jurisdiction and enforcement of international tribunal decisions on these issues. Furthermore, the applicability of the law on countermeasures to cyber-attack requires further research. However, the approach described represents a viable way to address existing concerns regarding attribution. If the international community adopts this model and it proves successful, that may enable a greater focus on other impediments to effectively dealing with the problem of cyber-attack.” (Payne e Finlay, 2017, p. 568)')}, {'id': 'f9e3e5fc', 'content': ('Creating an international attribution mechanism would promote collective responses and enhance the legitimacy of attributions.', '“Second, the creation of an international attribution mechanism would signal the growing interest of States in collective attribution, as broad condemnation and multilateral responses are more likely to promote accountability than the reactions of a single State. Collective attribution is most effective when there is a high level of confidence in the initial attribution determination. Such confidence can derive from close relations among relevant States, such as ongoing cooperation between their intelligence agencies, or through legitimacy-enhancing measures, like transparency.” (Shany e Schmitt, 2020, p. 220)')}, {'id': '07bb2fbd', 'content': ('A Probabilistic Approach is Necessary for Attribution in Cyberattacks.', '“We must realize that attribution may not always be perfect due to purposeful misdirection or limitations of the analysis itself. This was illustrated by the attack on Sony Pictures Entertainment in November 2014. A hacker group calling itself the “Guardians of Peace” released confidential Sony data onto the Internet, including personal employee data, vast email and password files, internal documents and communications, unreleased copies of motion pictures, and much more. There are two conflicting theories of attribution: one suggests that the North Korean government was behind the attack, given the similarity of the malware used to that used in previous attacks by the North Koreans;19 the other, based on linguistics analysis, suggests that Russians conducted the attack.20 There is no conclusive proof supporting either theory, only circumstantial evidence based on the conventional triad of means, motives, and opportunity. To address this, we must resort to a probabilistic approach and define standards of attributions based on the confidence levels of attribution and permissible retaliation to prevent the disproportionate response from escalating into a kinetic conflict.” (Goel, 2020, p. 94)')}, {'id': '61c1c38c', 'content': ('Future governance models may facilitate credible transnational cyber attribution despite existing challenges.', '“Future work should continue to seek a better understanding of how governance models, including an independent network of researchers based in academia, civil society, and business might help resolve the issues flagged above so that responsible parties can be held accountable. Despite the capacity of advanced and persistent threat actors, the need to protect intelligence sources and methods, and conflicting nationalistic approaches we believe that movement toward transnational, independent, credible attributions to “who did it” is possible.” (Kuerbis et al., 2022, p. 234)')}, {'id': '80822d28', 'content': ('Timing and coordination of cyber-attacks indicate potential state involvement.', '“The first category of significant indirect proof which can be considered during the process of attribution is the timing and coordination of the cyber-attacks. The more the attack’s timing is orchestrated and the more it appears to be well-coordinated overall, the higher the probability of a state’s involvement. A telling sign is how well the cyber-attacks are coordinated with events outside of cyberspace, especially when they are not publicly predictable, as a conventional military campaign would be. In such cases, the cyber-attacks can easily supplement the operations on the ground and multiply their effect. Without at least a certain degree of exchange of information between a sponsoring state and the perpetrators, a cyber campaign cannot be well-timed and coordinated.” (Kadlecová, 2018, p. 43)')}]}

def get_headings_for_clusters(clusters=clusters_to_test):
    aggregated_results = []
    # Loop over the clusters dictionary
    for cluster_key, cluster_value in clusters.items():
        # Construct the data for this cluster
        data = {item["id"]: item["content"] for item in cluster_value}  # Full tuple content for replacement

        # Format the data for the API prompt
        data_str = "\n".join([f"id = {key}: topic_sentence ={value[0]}" for key, value in data.items()])  # Use first element (summary)
        print('data string')
        
        # Call the API (replace this with actual API call)
        result_text = call_openai_api(function='get_headings', data=data_str, id='')
        print("result_text",type(result_text))


        # Parse the API result text to a dictionary if it's in JSON format
        if isinstance(result_text, str):
            try:
                result_text = json.loads(result_text)  # Convert to a dictionary
            except json.JSONDecodeError as e:
                print(f"Failed to decode API response: {e}")
                continue

        # Replace ids with paragraph content (both tuple elements)
        updated_structure = replace_ids_with_content(result_text, cluster_value)

        # Append parsed result to the aggregated results
        aggregated_results.append(updated_structure)

        print("aggregated_results\n", aggregated_results)
    # Use the overarching theme extracted from the first cluster
    overarching_theme = aggregated_results[0]["overarching_theme"] if aggregated_results else "Unknown Theme"


    return aggregated_results

def replace_ids_with_content(structure, clusters):
    # Extract the overarching theme from the first entry in the structure
    overarching_theme = structure["structure"][0]["title"] if structure["structure"] and structure["structure"][0]["heading"] == 'h1' else "Unknown Theme"


    # Iterate over the structure and replace paragraph_ids with corresponding content (both parts of the tuple)
    # Create a dictionary to map IDs to their tuple content (both topic sentence and full content)
    id_to_content = {item['id']: item['content'] for item in clusters}

    # Iterate over the structure and replace paragraph_ids with corresponding content
    for entry in structure["structure"]:
        if 'paragraph_ids' in entry:
            # Initialize new lists to hold topic sentences and paragraphs
            topic_sentences = []
            paragraphs = []

            # Replace each paragraph_id with its corresponding topic sentence and paragraph content
            for par_id in entry["paragraph_ids"]:
                if par_id in id_to_content:
                    topic_sentence, paragraph_content = id_to_content[par_id]
                    topic_sentences.append(topic_sentence)  # Add the topic sentence
                    paragraphs.append(paragraph_content)  # Add the full paragraph
                else:
                    topic_sentences.append(f"Topic sentence for {par_id} not found")
                    paragraphs.append(f"Full content for {par_id} not found")

            # Add topic sentences and paragraphs back into the structure
            entry["topic_sentence"] = " ".join(topic_sentences)  # Join sentences into a single string
            entry["paragraph_ids"] = " ".join(paragraphs)  # Join paragraphs into a single string

    # Add the overarching theme to the structure
    structure["overarching_theme"] = overarching_theme
    return structure


def get_context(data, current_heading):
    """
    This function generates the context for the current heading based on its level, up to h5.
    """
    context = ""
    # Tracks the parent headings
    parent_context = []

    # Loop through the structure to build the context
    for heading in data['structure']:
        # Check if it's an h1 heading (Overarching theme and h1)
        if heading['heading'] == 'h1':
            parent_context.append(f"Main Heading (h1): {heading['title']}")

        # Add context for h2, h3, h4, and h5
        if heading == current_heading:
            if current_heading['heading'] == 'h2':
                parent_context.append(f"Subheading (h2): {current_heading['title']}")
            elif current_heading['heading'] == 'h3':
                parent_context.append(f"Sub-subheading (h3): {current_heading['title']}")
            elif current_heading['heading'] == 'h4':
                parent_context.append(f"Sub-sub-subheading (h4): {current_heading['title']}")
            elif current_heading['heading'] == 'h5':
                parent_context.append(f"Sub-sub-sub-subheading (h5): {current_heading['title']}")
            break

    # Combine overarching theme and parent headings to create full context
    context = f"Overarching theme: {data['overarching_theme']}\n" + "\n".join(parent_context)

    return context

def write_and_export_sections( filename=r"C:\Users\luano\Downloads\AcAssitant\Files\Thematic_Review",export_to=['doc', 'html']):
    # input(replace_ids_with_content(structure=to_be_replaced,clusters=clusters_to_test[0]))
    data=get_headings_for_clusters()

    for data_item in data:
        theme = data_item.get('overarching_theme', 'No Theme')
        data_wrote = []

        # Iterate through the structure and call the OpenAI API
        for idx, heading in enumerate(data_item.get('structure', [])):
            # Ensure heading has the 'heading' key before processing
            if 'heading' in heading:
                # Generate context for the current heading
                context = get_context(data_item, heading)

                # Concatenate context and data for the API request
                data_to_send = concatenate_context_and_data(heading, context)
                print(data_to_send)
                # Call the OpenAI API with the provided function and data
                result = call_openai_api(data=data_to_send, id=f'heading-{idx}', function='thematic_review')
                data_wrote.append(result)
            else:
                print(f"Skipping entry at index {idx} as it doesn't have a 'heading' key.")

        # Prepare the final structure for export
        final_structure = {
            'overarching_theme': theme,
            'structure': data_wrote
        }
        print('final structure')
        # Parse the results from OpenAI API to match the structure expected by export_results
        for item in data_wrote:
            if isinstance(item, str):
                try:
                    parsed_item = json.loads(item)  # Parse if item is a JSON string
                    final_structure['structure'].append(parsed_item)
                except json.JSONDecodeError:
                    print(f"Error parsing item: {item}")
            elif isinstance(item, dict):
                final_structure['structure'].append(item)  # If it's already a dict, no need to parse

        # Ensure that final structure is correct for export
        print('Final structure:', final_structure)

        # Adjust the filename to be unique for each theme (optional)
        unique_filename = f"{filename}_{theme.replace(' ', '_')}"

        # Call the export_results function to handle the export
        export_results(structure=final_structure, filename=unique_filename, export_to=export_to)


def concatenate_context_and_data(heading, context):
    """
    This function concatenates the context with the heading's data for the final request.
    """
    # Combine context with the heading's data to create the full input for the API
    combined_data = {
        "context": context,
        "title": heading['title'],
        "topic_sentence_and_paragraph": f'topic sentenced:{heading.get('topic_sentence', [])}, references:{heading.get('paragraph_ids', [])}',
    }

    return combined_data

class QdrantHandler:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant_client = QdrantClient(url=qdrant_url)

    def create_collection(self, paper_id, vector_size=3072):
        """Create a collection in Qdrant based on a given paper ID if it does not exist."""
        collection_name = f"paper_{paper_id}"

        # Check if the collection already exists
        try:
            self.qdrant_client.get_collection(collection_name)
            print(f"Collection '{collection_name}' already exists.")

            return False  # Collection already exists
        except Exception as e:
            print(f"Collection '{collection_name}' not found. Creating new collection.")

            sparse_vectors = {
                "paragraph_text": models.SparseVectorParams(
                    modifier="idf"  # Use IDF for sparse vector search
                ),
                "paragraph_title": models.SparseVectorParams(
                    modifier="idf"  # Use IDF for sparse vector search
                ),
                "section_title": models.SparseVectorParams(
                    modifier="idf"  # Use IDF for sparse vector search
                )
            }

            # HNSW configuration for high-accuracy vector search
            hnsw_config = models.HnswConfigDiff(
                ef_construct=512,
                m=64
            )

            # Create the collection with vectors and sparse indexing
            self.qdrant_client.create_collection(

                collection_name=collection_name,
                vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),

                sparse_vectors_config=sparse_vectors,  # Correctly use sparse_vectors
                hnsw_config=hnsw_config,
                on_disk_payload=False  # Store payload data on disk to save RAM
            )

            # Create full-text indexes on paragraph_text, paragraph_title, and section_title
            text_fields = ["paragraph_text", "paragraph_title", "section_title"]
            for field in text_fields:
                self.qdrant_client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=models.TextIndexParams(
                        type="text",
                        tokenizer=models.TokenizerType.WORD,
                        min_token_len=2,
                        max_token_len=15,
                        lowercase=True
                    )
                )

            print(f"Collection '{collection_name}' created successfully with vector and full-text search.")
            return True  # Collection was newly created

    def append_data(self, collection_name, paragraph_count,article_title,section_title, paragraph_title, paragraph_text, paragraph_blockquote,
                    custom_id,text_embedding):
        """
        Insert embeddings for paragraph title and paragraph text into the collection with proper handling for both vectors.
        """

        # Use UUID or hash as point ID (this will be the actual point ID)
        paragraph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, custom_id))

        # Structure the payload, storing custom ID and other metadata
        payload = {
            "article_title":article_title,
            "section_title": section_title,
            "paragraph_title": paragraph_title,
            "paragraph_text": paragraph_text,
            "paragraph_blockquote": paragraph_blockquote,  # Include blockquote information
            "custom_id": custom_id,  # Store the custom ID in the payload
            "paragraph_count":paragraph_count
        }

        # Insert data into Qdrant with both title and text embeddings
        operation_info = self.qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=paragraph_id,  # Use UUID as point ID
                    vector=text_embedding,  # Insert the text embedding for the paragraph text
                    payload=payload  # Store metadata, including custom ID
                )
            ]
        )

        print(
            f"Inserted data for paragraph '{paragraph_title}' under section '{section_title}' with custom ID '{custom_id}'.")
        return operation_info

    def cluster_paragraphs(self, collection_names, n_clusters=None, max_clusters=10):
        """
        Perform clustering on paragraph vectors from multiple collections in Qdrant and group paragraphs based on their vector similarity.
        If a valid number of clusters is provided, use that number for clustering.
        Otherwise, automatically detect the optimal number of clusters using the Elbow Method.

        Parameters:
            collection_names (list): A list of Qdrant collection names where paragraphs are stored.
            n_clusters (int, optional): The number of clusters to use. If None, the optimal number of clusters will be calculated.
            max_clusters (int): The maximum number of clusters to test for the optimal k. Default is 10.

        Returns:
            clustered_paragraphs (dict): A dictionary where each key is a cluster label and each value is a list of paragraph texts.
        """

        paragraph_vectors = []
        paragraph_data = []  # List to store both the title and text as a tuple

        # Step 1: Fetch vectors and corresponding paragraph texts from each collection
        for collection_name in collection_names:
            try:
                # Retrieve all points with vectors from the collection using scroll (no need for IDs)
                scroll_result = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    with_payload=True,
                    with_vectors=True,  # Retrieve vectors
                    limit=1  # Adjust the limit as needed
                )[0][0]
            except Exception as e:
                print('error: ', e)
                continue

            vector = scroll_result.vector  # Assuming "text_embedding" is the vector field
            text = scroll_result.payload['paragraph_text']  # Extract paragraph text from payload
            title = scroll_result.payload['paragraph_title']  # Extract paragraph title from payload

            if vector and text and title:

                paragraph_id = str(uuid.uuid4()).split('-')[0]
                paragraph_vectors.append(vector)
                paragraph_data.append({'id':paragraph_id,'content':(title, text)})  # Store tuple (title, text)

        # Step 2: Convert the paragraph_vectors list to a NumPy array
        paragraph_vectors = np.array(paragraph_vectors)

        # Step 3: Adjust max_clusters to ensure it does not exceed the number of samples
        num_paragraphs = len(paragraph_vectors)
        max_clusters = min(max_clusters, num_paragraphs)

        # Step 4: Check if n_clusters is provided; if not, calculate optimal k using Elbow method
        if n_clusters is None:
            print("No number of clusters provided, calculating the optimal number using Elbow method.")
            kmeans = KMeans()
            visualizer = KElbowVisualizer(kmeans, k=(2, max_clusters), timings=False)

            # Fit the data to the visualizer to calculate the optimal k
            visualizer.fit(paragraph_vectors)

            # Fetch the inertia (distortion scores) and make sure they match the k range
            inertia = visualizer.k_scores_
            k_values = range(2, len(inertia) + 2)  # Adjust k_values to match the length of inertia

            # Automatically detect the elbow point programmatically
            kneedle = KneeLocator(k_values, inertia, curve="convex", direction="decreasing")
            n_clusters = kneedle.elbow

            # If no elbow point is detected, fallback to a default value (e.g., 2)
            if n_clusters is None:
                print("No elbow point detected, using default k=2")
                n_clusters = 2

        print(f"Using {n_clusters} clusters for K-means clustering.")

        # Step 5: Perform K-means clustering with the chosen number of clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(paragraph_vectors)

        # Step 6: Group paragraphs based on their cluster labels
        clustered_paragraphs = {i: [] for i in range(n_clusters)}
        for label, paragraph_info in zip(cluster_labels, paragraph_data):
            clustered_paragraphs[label].append(paragraph_info)  # Append the tuple (title, text)

        return clustered_paragraphs

    def classify_paragraphs(self, collection_name, section_titles):
        """
        Classify paragraphs into the respective section titles based on similarity between paragraph embeddings
        and section title embeddings.

        Parameters:
            collection_name (str): The name of the Qdrant collection containing the paragraphs.
            section_titles (list): A list of section titles to classify paragraphs into.

        Returns:
            classified_paragraphs (dict): A dictionary where keys are section titles and values are lists of classified paragraphs.
        """

        # Step 1: Fetch all paragraph vectors and text from Qdrant
        all_points = self.qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,  # Fetch in batches if necessary
            with_payload=True,
            with_vectors=True  # Retrieve vectors and payloads
        ).points

        # Extract paragraph vectors and corresponding paragraph texts
        paragraph_vectors = []
        paragraph_texts = []

        for point in all_points:
            vector = point.vector.get("text_embedding")  # Assuming "text_embedding" is the vector field
            text = point.payload.get("paragraph_text")  # Extract paragraph text from payload

            if vector and text:
                paragraph_vectors.append(vector)
                paragraph_texts.append(text)

        # Step 2: Create embeddings for the section titles
        section_embeddings = [self.embed_section_title(title) for title in
                              section_titles]  # Assume you have a function to embed section titles

        # Step 3: Initialize a dictionary to store classified paragraphs
        classified_paragraphs = {section_title: [] for section_title in section_titles}

        # Step 4: Classify each paragraph by comparing its vector to the section title embeddings
        for paragraph_vector, paragraph_text in zip(paragraph_vectors, paragraph_texts):
            # Compute the cosine similarity between paragraph vector and all section title vectors
            similarities = cosine_similarity([paragraph_vector], section_embeddings)[0]

            # Find the index of the section title with the highest similarity score
            best_section_idx = similarities.argmax()

            # Assign the paragraph to the most similar section title
            best_section_title = section_titles[best_section_idx]
            classified_paragraphs[best_section_title].append(paragraph_text)

        return classified_paragraphs

    def check_valid_embeddings(self):

        try:
            # Get all collections
            all_collections = self.qdrant_client.get_collections().collections

            # Check if there are any collections
            if not all_collections:
                return "No collections found in the database."

            # Retrieve the first collection name
            for collection in all_collections:
                for a in collection.dict():

                    print(a)

                collection_info = self.qdrant_client.get_collection(collection_name=collection.name)
                # self.qdrant_client.delete_collection(collection_name=collection.name)
                print(collection_info)
                # return collection_info
        except Exception as e:
            return f"Error retrieving collections: {str(e)}"

    def advanced_search(self, collection_name: str, query_vector: Optional[List[float]] = None,
                        top_k: Optional[int] = None,
                        filter_conditions: Optional[Dict[str, str]] = None, score_threshold: float = 0.60,
                        with_payload: bool = True, with_vectors: bool = False, hnsw_ef: int = 512, exact: bool = False,
                        keywords: Optional[List[str]] = None) -> Dict[str, List]:
        """
        Perform an advanced search in the Qdrant collection using hybrid search methods
    with sparse embeddings and dense vectors, applying rescoring mechanisms.

    Keyword Filtering:
    ------------------
    The search allows sophisticated filtering based on keywords. These keywords can be provided
    as a list and used for rescoring results based on their presence in the section title, paragraph title,
    and paragraph text. The following options are available for keyword filtering:

    1. **Keyword List**: Provide a list of keywords that will be used to rescore results if found in the
       section title, paragraph title, or text.
       Example:
       ```python
       keywords = ["machine learning", "artificial intelligence", "deep learning"]
       ```

    2. **Logical Operators for Keywords**:
       - You can implement logical operators (AND/OR) using multiple keyword lists or dictionaries.
       - **AND**: Rescore if *all* keywords in a group are found in the text.
       - **OR**: Rescore if *any* keyword from a group is found.

       Example:
       ```python
       keywords = {
           "AND": ["machine learning", "neural networks"],  # All keywords must be found
           "OR": ["deep learning", "AI"]  # Any keyword can be found for a boost
       }
       ```

    3. **Keyword Weighting**:
       - You can assign different weights to specific keywords to emphasize their importance in the rescoring.
       - Higher weights will result in a greater score boost when the keyword is found in the text.
       - These weights can also be field-specific (e.g., higher weights if found in the section title).

       Example:
       ```python
       keywords = {
           "neural networks": 0.3,
           "machine learning": 0.2,
           "deep learning": 0.5
       }
       ```

    4. **Field-Specific Keyword Scoring**:
       - Keywords can be matched in different fields with custom weights applied based on where the keyword
         is found:
           - **section_weight**: The weight applied when a keyword is found in the section title.
           - **paragraph_title_weight**: The weight applied when a keyword is found in the paragraph title.
           - **text_weight**: The weight applied when a keyword is found in the paragraph text.

       Example:
       ```python
       section_weight = 0.5  # Boost more for matches in section titles
       paragraph_title_weight = 0.4  # Medium boost for matches in paragraph titles
       text_weight = 0.2  # Lower boost for matches in the main text
       ```

    5. **Proximity Search** (if implemented):
       - Proximity-based rescoring can be added to give higher relevance to results where keywords appear
         closer together in the text. This can be useful in cases where keyword proximity increases relevance.

       Example (not implemented in this version):
       ```python
       proximity_threshold = 10  # Rescore if keywords appear within 10 words of each other
       ```

    Parameters:
    -----------
    collection_name : str
        The name of the Qdrant collection to search in.

    query_vector : Optional[List[float]], optional
        The dense vector used for semantic search. Default is None.

    top_k : Optional[int], optional
        The maximum number of results to return. Default is None.

    filter_conditions : Optional[Dict[str, str]], optional
        Additional filter conditions for the search, such as exact match or range filters.

    score_threshold : float, optional
        The minimum similarity score for results. Default is 0.60.

    with_payload : bool, optional
        Whether to return the payload along with search results. Default is True.

    with_vectors : bool, optional
        Whether to return vectors with search results. Default is False.

    hnsw_ef : int, optional
        Parameter for controlling the efficiency of the HNSW algorithm. Default is 512.

    exact : bool, optional
        Whether to perform exact search rather than approximate search. Default is False.

    keywords : Optional[List[str]], optional
        A list or dictionary of keywords to use for rescoring the search results.
        Keywords can be provided with optional weights or grouped with logical operators (AND/OR).
        Default is None.

    section_weight : float, optional
        Weight applied to score boosts when keywords are found in the section title. Default is 0.5.

    paragraph_title_weight : float, optional
        Weight applied to score boosts when keywords are found in the paragraph title. Default is 0.4.

    text_weight : float, optional
        Weight applied to score boosts when keywords are found in the paragraph text. Default is 0.2.

    Returns:
    --------
    Dict[str, List]
        A dictionary containing the processed search results, including section titles, paragraph titles,
        paragraph text, blockquotes, and rescored values.
        """

        # Initialize the processed_results variable as a defaultdict
        processed_results = defaultdict(list)

        # Define optional filtering if provided
        query_filter = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                if isinstance(value, dict) and "range" in value:
                    must_conditions.append(models.RangeCondition(
                        key=key,
                        range=models.Range(
                            gte=value["range"].get("gte"),
                            lte=value["range"].get("lte")
                        )
                    ))
                else:
                    must_conditions.append(models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    ))
            query_filter = models.Filter(must=must_conditions)

        # Define search parameters for HNSW ANN search
        search_params = models.SearchParams(
            hnsw_ef=hnsw_ef,
            exact=exact
        )

        try:
            # Perform the query
            results = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_vector,  # Dense vector search for semantic matching
                with_payload=with_payload,
                with_vectors=with_vectors,
                query_filter=query_filter,  # Apply any filters
                search_params=search_params,
                score_threshold=score_threshold,
            ).points
        except Exception as e:
            logging.error(f"Error during query to collection {collection_name}: {e}")
            return processed_results  # Return empty results on failure

        if not results:
            logging.info(f"No results found for collection: {collection_name}")
            return processed_results

        # Process results and apply rescoring
        for result in results:
            payload = result.payload
            score = result.score  # Qdrant similarity score

            # Call _rescore_result and check if it returns None (i.e., a NOT keyword was found)
            adjusted_score = self._rescore_result(
                payload=payload,
                initial_score=score,
                keywords=keywords,
                section_weight=0.3,
                paragraph_title_weight=0.2,
                text_weight=0.1
            )
            if adjusted_score is None:
                # Skip the result if _rescore_result indicates a NOT keyword match
                continue

            # Append results only if the paragraph passed the "NOT" filter and has been rescored
            processed_results['section_title'].append(payload.get('section_title', "N/A"))
            processed_results['paragraph_title'].append(payload.get('paragraph_title', "N/A"))
            processed_results['paragraph_text'].append(payload.get('paragraph_text', "N/A"))
            processed_results['paragraph_blockquote'].append(payload.get('paragraph_blockquote', "N/A"))
            processed_results['rescore'].append(adjusted_score)

        # Rescore and sort the results
        self._sort_results(processed_results)
        return processed_results

    def _rescore_result(self, payload: Dict[str, str], initial_score: float, keywords: Optional[Dict[str, List[str]]],
                        section_weight: float = 0.5, paragraph_title_weight: float = 0.4, text_weight: float = 0.2) -> \
    Optional[float]:
        """
        Rescore the result based on the presence of keywords in the section title, paragraph title, and text,
        supporting AND/OR/NOT logic for keyword matching. Returns None if a NOT keyword is found.
        """
        section_title = payload.get('section_title', "")
        paragraph_title = payload.get('paragraph_title', "")
        paragraph_text = payload.get('paragraph_text', "")
        if keywords is not None:
            # Handle "NOT" logic - exclude results if any keyword in the NOT group is found
            if "NOT" in keywords:
                for keyword in keywords["NOT"]:
                    if keyword.lower() in section_title.lower() or \
                            keyword.lower() in paragraph_title.lower() or \
                            keyword.lower() in paragraph_text.lower():
                        # Return None to indicate exclusion if a NOT keyword is found
                        return None

            adjusted_score = initial_score

            # Handle "AND" logic - all keywords in the AND group must appear
            if "AND" in keywords:
                all_keywords_found = all(
                    keyword.lower() in section_title.lower() or
                    keyword.lower() in paragraph_title.lower() or
                    keyword.lower() in paragraph_text.lower()
                    for keyword in keywords["AND"]
                )
                if all_keywords_found:
                    adjusted_score += section_weight  # Adjust based on how you want to boost AND logic

            # Handle "OR" logic - any keyword in the OR group can appear
            if "OR" in keywords:
                any_keyword_found = any(
                    keyword.lower() in section_title.lower() or
                    keyword.lower() in paragraph_title.lower() or
                    keyword.lower() in paragraph_text.lower()
                    for keyword in keywords["OR"]
                )
                if any_keyword_found:
                    adjusted_score += paragraph_title_weight  # Adjust based on OR logic

            return adjusted_score
        else:
            return initial_score

    def _sort_results(self, processed_results: defaultdict) -> None:
        """
        Sort the processed results based on the adjusted score in descending order.
        """
        sorted_results = sorted(zip(
            processed_results['section_title'],
            processed_results['paragraph_title'],
            processed_results['paragraph_text'],
            processed_results['paragraph_blockquote'],
            processed_results['rescore']
        ), key=lambda x: x[-1], reverse=True)

        if sorted_results:
            (processed_results['section_title'],
             processed_results['paragraph_title'],
             processed_results['paragraph_text'],
             processed_results['paragraph_blockquote'],
             processed_results['rescore']) = zip(*sorted_results)

    def qdrant_collections(self,col_name):
        collection = [collection.name for collection in self.qdrant_client.get_collections().collections if collection.name.split("_")[-1]==col_name]
        return collection

    def update_collection_config(self,collection_name):
        # Initialize Qdrant client
        client = QdrantClient(url="http://localhost:6333")

        # Update the collection's vector configuration
        client.update_collection(
            collection_name=collection_name,
            vectors={
                "dense_vector": models.VectorParams(
                    size=3072,  # Size for text-embedding-3-large
                    distance=models.Distance.COSINE  # Cosine similarity for dense vectors
                )
            },
            sparse_vectors={
                "text": models.SparseVectorParams(
                    modifier="idf"  # The correct way to specify IDF in sparse vectors
                )
            }
        )

        print(f"Updated collection '{collection_name}' successfully.")

        print(f"Collection '{collection_name}' updated successfully.")
    def find_collection_by_custom_id(self, custom_id):
        """
        Find the collection name associated with a given custom_id (paper ID).
        """
        try:
            # List all available collections
            collections = self.qdrant_client.get_collections().collections
            # Iterate over collections to find the one corresponding to the custom_id
            for collection in collections:
                collection_name = collection.name

                # Assuming `custom_id` is stored as payload in points of this collection
                result, next_page_token = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="custom_id",
                                match=models.MatchValue(value=custom_id)
                            )
                        ]
                    ),
                    limit=1  # Limit to one result
                )

                # Check if any points are found
                if result:
                    return collection_name

            # If no collection with the custom_id found
            return None

        except UnexpectedResponse as e:
            print(f"Error occurred: {e}")
            return None
