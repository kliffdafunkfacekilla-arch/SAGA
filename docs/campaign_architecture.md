# The SAGA Dynamic Campaign Framework

**Core Concept:** A procedural narrative engine that bounds highly reactive, player-driven micro-stories within a structured, overarching campaign spine.

## 1. The Campaign Spine (Fixed Nodes)
- The overarching story is divided into 3 Acts.
- Each Act is anchored by hardcoded Major Plot Points (Fixed Slots). These are the mandatory narrative milestones that drive the grand campaign forward.

## 2. The Dynamic Journey (Variable Slots)
- Between each Major Plot Point, the engine generates a random number of Dynamic Slots to create the "Story Map."
- These empty slots represent the journey, localized events, and obstacles the players must navigate to reach the next fixed milestone.

## 3. Contextual Seed Generation
- When a scene renders and an empty Dynamic Slot is active, the background AI evaluates the current world data, terrain tags, and player stats.
- It procedurally generates 2-3 localized Story Seeds (e.g., a hungry urchin, an injured courier, a hostile guard) that logically fit the current environment.

## 4. Player Agency & Lock-In
- The players organically choose which seed to interact with.
- Once engaged, that specific seed is locked into the Dynamic Slot, and the unchosen seeds are culled.
- The AI Director then fleshes out the chosen seed into a full encounter, rendering the scene and narrating the resolution as the players navigate it.

## 5. The Ripple Effect (World Memory)
- Once the encounter is resolved, the Dynamic Slot is marked complete and crossed off the Story Map.
- The outcome of that slot permanently updates the world state and is saved as Generation Data.
- Moving forward, the engine uses these completed slots as context. When the world simulates its next tick or generates future seeds, it factors in past player choices, causing the narrative to autonomously weave itself into a coherent, dynamic campaign.
