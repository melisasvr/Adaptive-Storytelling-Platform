import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

class Mood(Enum):
    ADVENTUROUS = "adventurous"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    DARK = "dark"
    HUMOROUS = "humorous"
    CONTEMPLATIVE = "contemplative"
    TENSE = "tense"

class EngagementLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class UserChoice:
    choice_id: str
    choice_text: str
    timestamp: datetime
    response_time: float
    mood_impact: Dict[Mood, float] = field(default_factory=dict)

@dataclass
class UserProfile:
    user_id: str
    preferred_moods: List[Mood] = field(default_factory=list)
    choice_history: List[UserChoice] = field(default_factory=list)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    narrative_preferences: Dict[str, float] = field(default_factory=dict)
    
    def add_choice(self, choice: UserChoice):
        self.choice_history.append(choice)
        self._update_preferences(choice)
    
    def _update_preferences(self, choice: UserChoice):
        # Update mood preferences based on choices
        for mood, impact in choice.mood_impact.items():
            if mood.value not in self.narrative_preferences:
                self.narrative_preferences[mood.value] = 0
            self.narrative_preferences[mood.value] += impact * 0.1

class StoryElement:
    def __init__(self, element_id: str, element_type: str, content: str, 
                 tags: List[str] = None, mood_weights: Dict[Mood, float] = None):
        self.element_id = element_id
        self.element_type = element_type
        self.content = content
        self.tags = tags or []
        self.mood_weights = mood_weights or {}
        self.usage_count = 0
        self.relationships = {}

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}  # element_id -> StoryElement
        self.relationships = {}  # (from_id, to_id) -> relationship_type
        
    def add_element(self, element: StoryElement):
        self.nodes[element.element_id] = element
    
    def add_relationship(self, from_id: str, to_id: str, relationship_type: str):
        self.relationships[(from_id, to_id)] = relationship_type
        
    def get_related_elements(self, element_id: str, relationship_type: str = None) -> List[StoryElement]:
        related = []
        for (from_id, to_id), rel_type in self.relationships.items():
            if from_id == element_id and (relationship_type is None or rel_type == relationship_type):
                if to_id in self.nodes:
                    related.append(self.nodes[to_id])
        return related
    
    def find_elements_by_mood(self, mood: Mood, threshold: float = 0.5) -> List[StoryElement]:
        return [element for element in self.nodes.values() 
                if element.mood_weights.get(mood, 0) >= threshold]

class UserEngagementTracker:
    def __init__(self):
        self.session_start = time.time()
        self.interaction_log = []
        self.current_mood = Mood.CONTEMPLATIVE
        
    def track_choice(self, choice_time: float, choice_id: str) -> EngagementLevel:
        self.interaction_log.append({
            'timestamp': time.time(),
            'choice_time': choice_time,
            'choice_id': choice_id
        })
        
        # Determine engagement based on response time
        if choice_time < 3:
            return EngagementLevel.HIGH
        elif choice_time < 10:
            return EngagementLevel.MEDIUM
        else:
            return EngagementLevel.LOW
    
    def infer_mood(self, recent_choices: List[UserChoice]) -> Mood:
        if not recent_choices:
            return self.current_mood
            
        mood_scores = {mood: 0 for mood in Mood}
        
        for choice in recent_choices[-5:]:  # Consider last 5 choices
            for mood, impact in choice.mood_impact.items():
                mood_scores[mood] += impact
        
        # Return mood with highest score
        return max(mood_scores, key=mood_scores.get) if mood_scores else self.current_mood

class NarrativeAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.story_templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, List[str]]:
        return {
            'plot_twists': [
                "Suddenly, {character} revealed they had been {revelation} all along.",
                "The {object} that {character} had been carrying was actually {true_nature}.",
                "What seemed like {appearance} was actually {reality}.",
            ],
            'character_interactions': [
                "{character1} looked at {character2} with {emotion}.",
                "'{dialogue}' {character1} said to {character2}.",
                "{character1} and {character2} found themselves {situation}.",
            ],
            'scene_transitions': [
                "The scene shifted to {location}, where {atmosphere}.",
                "Time passed, and now {character} found themselves {new_situation}.",
                "Meanwhile, in {location}, {event} was unfolding.",
            ]
        }
    
    def generate_narrative_element(self, element_type: str, context: Dict[str, Any], 
                                 user_mood: Mood) -> str:
        templates = self.story_templates.get(element_type, [])
        if not templates:
            return f"The story continues with {element_type}..."
        
        template = random.choice(templates)
        
        # Get mood-appropriate elements from knowledge graph
        mood_elements = self.knowledge_graph.find_elements_by_mood(user_mood)
        
        # Fill template with context and mood-appropriate elements
        filled_template = self._fill_template(template, context, mood_elements, user_mood)
        
        return filled_template
    
    def _fill_template(self, template: str, context: Dict[str, Any], 
                      mood_elements: List[StoryElement], user_mood: Mood) -> str:
        # Simple template filling logic
        replacements = {}
        
        # Get characters from context or mood elements
        characters = [elem for elem in mood_elements if elem.element_type == 'character']
        if characters:
            replacements['character'] = random.choice(characters).content
            replacements['character1'] = random.choice(characters).content
            replacements['character2'] = random.choice(characters).content
        else:
            replacements['character'] = "the protagonist"
            replacements['character1'] = "the hero"
            replacements['character2'] = "a mysterious figure"
        
        # Get locations
        locations = [elem for elem in mood_elements if elem.element_type == 'location']
        if locations:
            replacements['location'] = random.choice(locations).content
        else:
            replacements['location'] = "an unknown place"
        
        # Mood-specific replacements
        mood_specific = self._get_mood_specific_content(user_mood)
        replacements.update(mood_specific)
        
        # Add more generic replacements
        replacements.update({
            'object': 'a mysterious artifact',
            'revelation': 'hiding their true identity',
            'true_nature': 'a key to ancient secrets',
            'appearance': 'a simple choice',
            'reality': 'a test of character',
            'dialogue': 'The path ahead is uncertain',
            'new_situation': 'facing an unexpected challenge',
            'event': 'a crucial moment',
            'atmosphere': mood_specific.get('atmosphere', 'an air of mystery')
        })
        
        # Fill template
        for key, value in replacements.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template
    
    def _get_mood_specific_content(self, mood: Mood) -> Dict[str, str]:
        mood_content = {
            Mood.ADVENTUROUS: {
                'emotion': 'excitement',
                'atmosphere': 'energy filled the air',
                'situation': 'facing an unexpected challenge'
            },
            Mood.MYSTERIOUS: {
                'emotion': 'suspicion',
                'atmosphere': 'shadows danced mysteriously',
                'situation': 'shrouded in mystery'
            },
            Mood.ROMANTIC: {
                'emotion': 'longing',
                'atmosphere': 'a gentle warmth pervaded',
                'situation': 'sharing a tender moment'
            },
            Mood.DARK: {
                'emotion': 'dread',
                'atmosphere': 'an ominous presence loomed',
                'situation': 'confronting their darkest fears'
            },
            Mood.HUMOROUS: {
                'emotion': 'amusement',
                'atmosphere': 'laughter echoed through the space',
                'situation': 'in a hilariously awkward predicament'
            },
            Mood.CONTEMPLATIVE: {
                'emotion': 'thoughtfulness',
                'atmosphere': 'a serene calm settled over everything',
                'situation': 'lost in deep contemplation'
            },
            Mood.TENSE: {
                'emotion': 'anxiety',
                'atmosphere': 'tension crackled in the air',
                'situation': 'on edge and ready for anything'
            }
        }
        return mood_content.get(mood, {})

class DialogueAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.dialogue_styles = self._initialize_dialogue_styles()
    
    def _initialize_dialogue_styles(self) -> Dict[Mood, Dict[str, List[str]]]:
        return {
            Mood.ADVENTUROUS: {
                'greetings': ["Ready for an adventure?", "Let's see what lies ahead!"],
                'reactions': ["This is incredible!", "I didn't expect this!"],
                'questions': ["What do you think we should do?", "Are you ready for this?"]
            },
            Mood.MYSTERIOUS: {
                'greetings': ["Something isn't right here...", "There's more to this than meets the eye..."],
                'reactions': ["How curious...", "That's... unexpected."],
                'questions': ["What are you hiding?", "What's really going on here?"]
            },
            Mood.ROMANTIC: {
                'greetings': ["You look beautiful today", "I've been thinking about you"],
                'reactions': ["My heart is racing", "This feels like a dream"],
                'questions': ["Do you feel the same way?", "What does this mean for us?"]
            },
            Mood.DARK: {
                'greetings': ["The shadows grow longer...", "Something wicked this way comes..."],
                'reactions': ["This bodes ill", "I fear what lies ahead"],
                'questions': ["What darkness awaits?", "Can we survive this?"]
            },
            Mood.HUMOROUS: {
                'greetings': ["Well, this is awkward!", "Did someone say comedy?"],
                'reactions': ["That's hilarious!", "I can't stop laughing!"],
                'questions': ["Is this really happening?", "Are we seriously doing this?"]
            },
            Mood.CONTEMPLATIVE: {
                'greetings': ["I've been thinking...", "There's wisdom in silence"],
                'reactions': ["How fascinating...", "This requires careful thought"],
                'questions': ["What does this mean?", "Have you considered the implications?"]
            },
            Mood.TENSE: {
                'greetings': ["Stay alert", "Something's not right"],
                'reactions': ["We need to be careful", "The situation is escalating"],
                'questions': ["Are you ready?", "What's our next move?"]
            }
        }
    
    def generate_dialogue(self, character_id: str, dialogue_type: str, 
                         user_mood: Mood, context: Dict[str, Any]) -> str:
        style = self.dialogue_styles.get(user_mood, {})
        options = style.get(dialogue_type, ["..."])
        
        base_dialogue = random.choice(options)
        
        # Get character from knowledge graph
        character = self.knowledge_graph.nodes.get(character_id)
        if character:
            # Customize dialogue based on character traits
            base_dialogue = self._customize_for_character(base_dialogue, character)
        
        return base_dialogue
    
    def _customize_for_character(self, dialogue: str, character: StoryElement) -> str:
        # Simple customization based on character tags
        if 'formal' in character.tags:
            dialogue = dialogue.replace("you", "you, sir/madam")
        elif 'casual' in character.tags:
            dialogue = dialogue.lower()
        
        return dialogue

class VisualStyleAgent:
    def __init__(self):
        self.style_mappings = self._initialize_style_mappings()
    
    def _initialize_style_mappings(self) -> Dict[Mood, Dict[str, Any]]:
        return {
            Mood.ADVENTUROUS: {
                'color_palette': ['#FF6B35', '#F7931E', '#FFD23F'],
                'lighting': 'bright',
                'atmosphere': 'energetic'
            },
            Mood.MYSTERIOUS: {
                'color_palette': ['#2E1065', '#5D4E75', '#8B7EA8'],
                'lighting': 'dim',
                'atmosphere': 'ethereal'
            },
            Mood.ROMANTIC: {
                'color_palette': ['#FFB6C1', '#FFC0CB', '#FF69B4'],
                'lighting': 'warm',
                'atmosphere': 'soft'
            },
            Mood.DARK: {
                'color_palette': ['#1C1C1C', '#2F2F2F', '#4F4F4F'],
                'lighting': 'shadowy',
                'atmosphere': 'ominous'
            },
            Mood.CONTEMPLATIVE: {
                'color_palette': ['#6B73FF', '#9B59B6', '#3498DB'],
                'lighting': 'soft',
                'atmosphere': 'peaceful'
            },
            Mood.HUMOROUS: {
                'color_palette': ['#F39C12', '#E74C3C', '#2ECC71'],
                'lighting': 'bright',
                'atmosphere': 'playful'
            },
            Mood.TENSE: {
                'color_palette': ['#E74C3C', '#C0392B', '#922B21'],
                'lighting': 'harsh',
                'atmosphere': 'intense'
            }
        }
    
    def get_visual_style(self, mood: Mood) -> Dict[str, Any]:
        return self.style_mappings.get(mood, self.style_mappings[Mood.CONTEMPLATIVE])

class PersonalizedDiscovery:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
    
    def recommend_content(self, user_profile: UserProfile, 
                         current_context: Dict[str, Any]) -> List[StoryElement]:
        recommendations = []
        
        # Get user's preferred moods
        mood_preferences = user_profile.narrative_preferences
        
        # Find content matching preferences
        for mood_str, preference_score in mood_preferences.items():
            if preference_score > 0.3:  # Threshold for recommendations
                mood = Mood(mood_str)
                matching_elements = self.knowledge_graph.find_elements_by_mood(mood)
                
                # Filter out already heavily used content
                fresh_content = [elem for elem in matching_elements if elem.usage_count < 3]
                recommendations.extend(fresh_content[:2])  # Top 2 per mood
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def suggest_branching_paths(self, current_element: StoryElement, 
                              user_profile: UserProfile) -> List[Tuple[str, StoryElement]]:
        # Get related elements
        related = self.knowledge_graph.get_related_elements(current_element.element_id)
        
        # Score based on user preferences
        scored_paths = []
        for element in related:
            score = self._calculate_preference_score(element, user_profile)
            scored_paths.append((score, element))
        
        # Sort by score and return top paths
        scored_paths.sort(reverse=True)
        return [(f"Path to {elem.content}", elem) for score, elem in scored_paths[:3]]
    
    def _calculate_preference_score(self, element: StoryElement, 
                                   user_profile: UserProfile) -> float:
        score = 0
        
        # Score based on mood preferences
        for mood, weight in element.mood_weights.items():
            user_pref = user_profile.narrative_preferences.get(mood.value, 0)
            score += weight * user_pref
        
        # Bonus for less used content
        freshness_bonus = max(0, 1 - (element.usage_count * 0.2))
        score += freshness_bonus
        
        return score

class AdaptiveStorytellingPlatform:
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.narrative_agent = NarrativeAgent(self.knowledge_graph)
        self.dialogue_agent = DialogueAgent(self.knowledge_graph)
        self.visual_agent = VisualStyleAgent()
        self.discovery_agent = PersonalizedDiscovery(self.knowledge_graph)
        self.engagement_tracker = UserEngagementTracker()
        self.users = {}  # user_id -> UserProfile
        
        # Initialize with sample content
        self._initialize_sample_content()
    
    def _initialize_sample_content(self):
        # Sample characters
        hero = StoryElement("hero_1", "character", "Alex the Brave", 
                           tags=["heroic", "determined"], 
                           mood_weights={Mood.ADVENTUROUS: 0.8, Mood.TENSE: 0.6})
        
        mentor = StoryElement("mentor_1", "character", "Sage Eldara", 
                             tags=["wise", "mysterious"], 
                             mood_weights={Mood.MYSTERIOUS: 0.9, Mood.CONTEMPLATIVE: 0.7})
        
        villain = StoryElement("villain_1", "character", "Lord Shadowmere", 
                              tags=["evil", "powerful"], 
                              mood_weights={Mood.DARK: 0.9, Mood.TENSE: 0.8})
        
        # Sample locations
        forest = StoryElement("location_1", "location", "the Enchanted Forest", 
                             tags=["magical", "mysterious"], 
                             mood_weights={Mood.MYSTERIOUS: 0.7, Mood.ADVENTUROUS: 0.5})
        
        castle = StoryElement("location_2", "location", "the Dark Castle", 
                             tags=["ominous", "ancient"], 
                             mood_weights={Mood.DARK: 0.8, Mood.TENSE: 0.7})
        
        # Add more sample content for better recommendations
        love_interest = StoryElement("character_2", "character", "Elena the Enchantress", 
                                   tags=["mysterious", "alluring"], 
                                   mood_weights={Mood.ROMANTIC: 0.8, Mood.MYSTERIOUS: 0.6})
        
        comic_relief = StoryElement("character_3", "character", "Bumbling Bob", 
                                  tags=["funny", "clumsy"], 
                                  mood_weights={Mood.HUMOROUS: 0.9, Mood.ADVENTUROUS: 0.3})
        
        ancient_tome = StoryElement("item_1", "item", "the Ancient Tome of Secrets", 
                                   tags=["powerful", "mysterious"], 
                                   mood_weights={Mood.MYSTERIOUS: 0.8, Mood.CONTEMPLATIVE: 0.7})
        
        magic_sword = StoryElement("item_2", "item", "the Blazing Sword of Heroes", 
                                  tags=["powerful", "heroic"], 
                                  mood_weights={Mood.ADVENTUROUS: 0.9, Mood.TENSE: 0.6})
        
        # Add to knowledge graph
        for element in [hero, mentor, villain, forest, castle, love_interest, comic_relief, ancient_tome, magic_sword]:
            self.knowledge_graph.add_element(element)
        
        # Add relationships
        self.knowledge_graph.add_relationship("hero_1", "mentor_1", "guided_by")
        self.knowledge_graph.add_relationship("hero_1", "villain_1", "opposes")
        self.knowledge_graph.add_relationship("villain_1", "location_2", "resides_in")
    
    def create_user(self, user_id: str) -> UserProfile:
        user_profile = UserProfile(user_id)
        self.users[user_id] = user_profile
        return user_profile
    
    def process_user_choice(self, user_id: str, choice_text: str, 
                           response_time: float) -> Dict[str, Any]:
        if user_id not in self.users:
            self.create_user(user_id)
        
        user_profile = self.users[user_id]
        
        # Create choice record
        choice = UserChoice(
            choice_id=str(uuid.uuid4()),
            choice_text=choice_text,
            timestamp=datetime.now(),
            response_time=response_time,
            mood_impact=self._analyze_choice_mood_impact(choice_text)
        )
        
        # Update user profile
        user_profile.add_choice(choice)
        
        # Track engagement
        engagement = self.engagement_tracker.track_choice(response_time, choice.choice_id)
        
        # Infer current mood
        current_mood = self.engagement_tracker.infer_mood(user_profile.choice_history)
        
        return {
            'choice_id': choice.choice_id,
            'engagement_level': engagement,
            'inferred_mood': current_mood,
            'user_profile': user_profile
        }
    
    def _analyze_choice_mood_impact(self, choice_text: str) -> Dict[Mood, float]:
        # Simple keyword-based mood analysis
        mood_keywords = {
            Mood.ADVENTUROUS: ['explore', 'adventure', 'quest', 'journey', 'discover'],
            Mood.MYSTERIOUS: ['investigate', 'mystery', 'secret', 'hidden', 'unknown'],
            Mood.ROMANTIC: ['love', 'romance', 'heart', 'kiss', 'together'],
            Mood.DARK: ['fight', 'battle', 'dark', 'evil', 'danger'],
            Mood.HUMOROUS: ['joke', 'funny', 'laugh', 'silly', 'amusing']
        }
        
        mood_impact = {}
        choice_lower = choice_text.lower()
        
        for mood, keywords in mood_keywords.items():
            impact = sum(0.2 for keyword in keywords if keyword in choice_lower)
            if impact > 0:
                mood_impact[mood] = min(impact, 1.0)
        
        return mood_impact
    
    def generate_adaptive_content(self, user_id: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        if user_id not in self.users:
            self.create_user(user_id)
        
        user_profile = self.users[user_id]
        current_mood = self.engagement_tracker.infer_mood(user_profile.choice_history)
        context = context or {}
        
        # Generate narrative content
        narrative = self.narrative_agent.generate_narrative_element(
            'scene_transitions', context, current_mood)
        
        # Generate dialogue
        dialogue = self.dialogue_agent.generate_dialogue(
            'hero_1', 'reactions', current_mood, context)
        
        # Get visual style
        visual_style = self.visual_agent.get_visual_style(current_mood)
        
        # Get recommendations
        recommendations = self.discovery_agent.recommend_content(user_profile, context)
        
        return {
            'narrative': narrative,
            'dialogue': dialogue,
            'visual_style': visual_style,
            'recommendations': [elem.content for elem in recommendations],
            'current_mood': current_mood,
            'user_preferences': user_profile.narrative_preferences
        }

# Example usage and testing
def demo_platform():
    # Initialize platform
    platform = AdaptiveStorytellingPlatform()
    
    # Create a user
    user_profile = platform.create_user("demo_user")
    
    print("=== Adaptive Storytelling Platform Demo ===\n")
    
    # Simulate user choices
    choices = [
        ("I want to explore the mysterious forest", 2.5),
        ("Let's investigate the strange sounds", 1.8),
        ("I'll approach the dark figure cautiously", 4.2),
        ("Time to face the challenge head-on!", 1.2)
    ]
    
    for i, (choice_text, response_time) in enumerate(choices, 1):
        print(f"Choice {i}: '{choice_text}' (Response time: {response_time}s)")
        
        # Process choice
        choice_result = platform.process_user_choice("demo_user", choice_text, response_time)
        
        print(f"Engagement: {choice_result['engagement_level'].value}")
        print(f"Inferred Mood: {choice_result['inferred_mood'].value}")
        
        # Generate adaptive content
        content = platform.generate_adaptive_content("demo_user")
        
        print(f"Generated Narrative: {content['narrative']}")
        print(f"Character Dialogue: {content['dialogue']}")
        print(f"Visual Style: {content['visual_style']}")
        print(f"Recommendations: {', '.join(content['recommendations'])}")
        print(f"Current Mood: {content['current_mood'].value}")
        print("-" * 50)

if __name__ == "__main__":
    demo_platform()