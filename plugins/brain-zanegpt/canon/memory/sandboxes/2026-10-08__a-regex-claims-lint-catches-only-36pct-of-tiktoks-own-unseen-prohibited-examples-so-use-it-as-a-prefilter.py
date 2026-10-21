#!/usr/bin/env python3
"""Sandbox: how much of TikTok's OWN prohibited-claim examples does a keyword/regex claims linter catch? Deterministic, stdlib only.
Ground truth = quoted examples on TikTok Shop Seller University pages (read live 2026-10-08): "Requirements for Responsible Health-Related
Content" (14 prohibited, 3 regulated, 5 allowed phrases) and "Weight Management Guide" (labels assigned by the section each quote sits under).

HONEST CHRONOLOGY (this is exploratory, NOT a pre-registered test): v1 was written from the policy's RULE TEXT and run on the 14 health-page
prohibited examples (6/14). v2 was then tuned on those same 14 (so they are TRAINING data) and frozen. v2 was run once on the unlabeled
weight-guide quotes; labels were assigned afterwards from page context. No prediction was recorded before the held-out run, so the held-out
numbers are a measurement, not a confirmed prediction. The only recorded expectation: a regex linter misses indirect wording.
n=25 prohibited and 9 allowed held-out phrases (duplicates removed), plus 22 benign ad lines written earlier for other sandboxes.
"""
import re
# v1: written from the policy's RULE TEXT categories only (medical verbs on conditions; timeline+quantity weight promises;
# before/after body comparisons; steroid/GLP equivalence), before matching against any example phrase.
V1_MED=r"\b(cure[sd]?|treat[s]?|prevent[s]?|heal[s]?|alleviate[s]?|diagnos\w*)\b"
V1_COND=r"\b(disease|cancer|diabetes|anxiety|depression|ptsd|asthma|arthritis|infection|condition|illness)\b"
V1_WL=r"\b(lose|drop|burn|shed)\b.{0,25}\b(\d+\s*(?:lbs?|pounds?|kg)|fat|weight)\b"
V1_TIME=r"\b(in (?:a|\d+) (?:day|week|month)s?|overnight|instantly|fast|right away)\b"
V1_BA=r"\bsize \d+ to size \d+\b|\bbefore and after\b"
V1_EQ=r"\b(steroid|glp-?1|ozempic|wegovy)\b"
def lint_v1(s):
    s=s.lower(); out=[]
    if re.search(V1_MED,s) and re.search(V1_COND,s): out.append("medical")
    if re.search(V1_WL,s) and re.search(V1_TIME,s): out.append("weight-timeline")
    if re.search(V1_BA,s): out.append("before-after")
    if re.search(V1_EQ,s): out.append("equivalence")
    return out

# v2: tuned on the 14 health-page prohibited examples (so those are TRAINING data); frozen before the weight-guide held-out test.
MEDV=r"\b(cure[sd]?|treat\w*|prevent\w*|heal\w*|alleviate\w*|eases|ease|diagnos\w*|relie\w*|reverse\w*|disappear\w*|fights?)\b"
COND=r"\b(disease|cancer|diabetes|anxiety|depression|ptsd|post-traumatic|asthma|arthritis|infection|condition|illness|colds?|flu|psoriasis|eczema|acne|obes\w*|insomnia|adhd|symptoms?|migraines?)\b"
WL=r"\b(lose|drop|burn|shed|melt\w*|slim\w*|never worry about)\b.{0,30}\b(\d+\s*(?:lbs?|pounds?|kg)|fat|weight|legs?|belly|inches)\b"
TIME=r"\b(in (?:a|\d+) (?:day|week|month|hour)s?|overnight|instantly|fast|right away|quickly|effortless\w*)\b"
GAIN=r"\bgain\b.{0,12}\d+\s*(?:lbs?|pounds?|kg)\b"
BA=r"\bsize \d+ to (?:size )?\d+\b|\bbefore[- ]and[- ]after\b|\bno longer obese\b"
EQ=r"\b(steroids?|glp-?1|glucagon|ozempic|wegovy|mounjaro|semaglutide)\b"
SUPPRESS=r"\b(doctors? (?:do not|don't|dont) want you to know|big pharma|they don't want you)\b"
REGULATED=r"\b(may reduce (?:the )?risk|high in vitamin|rich in vitamin|supports? (?:healthy )?\w+|usda organic|gluten[- ]free|non-gmo|clinically proven)\b"
def lint_v2(s):
    t=s.lower(); out=[]
    if re.search(MEDV,t) and re.search(COND,t): out.append("medical")
    if (re.search(WL,t) and re.search(TIME,t)) or re.search(GAIN,t) or re.search(r"never worry about weight gain",t): out.append("weight-timeline")
    if re.search(BA,t): out.append("before-after")
    if re.search(EQ,t): out.append("equivalence")
    if re.search(SUPPRESS,t): out.append("suppression")
    if not out and re.search(REGULATED,t): out.append("regulated-warn")
    return out

TRAIN_PROH=["This supplement prevents heart disease.","This tea eases Post-Traumatic Stress Disorder (PTSD) symptoms.","Doctors do not want you to know about this product. My psoriasis disappeared!","This essential oil blend cures anxiety","Drink this juice to prevent colds.","Drop 10 pounds in a week with this supplement","Burn belly fat instantly with this tea","Take this snack daily and never worry about weight gain","No longer obese, thanks to this product!","Get slim legs right away when you use this lotion","Burn fat fast","This product helped me drop from size 16 to size 8","Gain 20 lbs of muscle fast","Works like anabolic steroids"]
TRAIN_REG=["May reduce risk of osteoporosis","High in vitamin C","Supports healthy digestion"]
TRAIN_OK=["food is fuel","designed to support","intended for","helps maintain"]
HELD_PROH=["Guaranteed weight loss in X days.","Rapid fat loss.","This product has GLP-1 activation.","GLP-1 mimic.","Works like steroids without the needle.","Legal roids.","gain 20 lbs of muscle fast","see results in 4 weeks","Lose weight fast!","This tea can help you prevent obesity","detox for weight loss","flattens belly fat","shrinks thighs","clinically approved","Formulated with CLA (Conjugated Linoleic Acid, a fatty acid) to help reduce body fat.","Infused with L-carnitine (an amino acid supplement) to enhance fat burning and boost energy during workouts.","Contains Forskolin (an extract from the Indian Coleus plant) to break down stored fat and promote weight loss.","Made with natural diuretics to help you shed water weight quickly.","gain X lbs of muscle","bulk fast","legal steroids","anabolic results","fat-burning","lose weight fast","Rapid fat loss"]
HELD_OK=["helps with muscle gain","supports building lean muscle","Enhances my energy","Helps me feel less sluggish","Supports my balanced diet","Helps me feel less bloated or constipated","Supports my overall well-being","Supports my balanced lifestyle","Helps me feel cleaner or more refreshed"]
HELD_PROH=list(dict.fromkeys(HELD_PROH))
BENIGN=["Wait, this actually works?","I found it on TikTok Shop.","Watch what happens next.","Grab yours before it sells out.","I've tried everything, and nothing cleaned my kitchen like this.","One spray, thirty seconds, and the stain is gone.","It's lightweight, it folds flat, and it fits in my bag.","My skin has never felt this smooth.","I was skeptical at first, but after one week I'm completely sold.","If you want a gift they'll actually use, tap the link below.","It charges in twenty minutes and lasts all day long.","Link's in my bio, and it's on sale right now.","Stop scrolling, this fixed my dry skin.","I wasted money on every mop until this one.","Your dog will lose it over this.","This costs less than lunch, and it changed my mornings.","Nobody told me my charger could do this.","Three seconds, and my sink is spotless.","I'm a trainer, and I never skip this.","Why is nobody talking about this?","Buy it before the price goes back up.","Is this the best gift under twenty dollars?"]
block=lambda f,s:[c for c in f(s) if c!="regulated-warn"]
def rec(f,L): return sum(bool(block(f,s)) for s in L)
print(f"v1 (rule text only) on 14 training prohibited: {rec(lint_v1,TRAIN_PROH)}/14")
print(f"v2 (tuned) on the same 14: {rec(lint_v2,TRAIN_PROH)}/14  [training data]; regulated warned {sum('regulated-warn' in lint_v2(s) for s in TRAIN_REG)}/3; allowed blocked {rec(lint_v2,TRAIN_OK)}/4")
hr=rec(lint_v2,HELD_PROH); n=len(HELD_PROH); fb=rec(lint_v2,HELD_OK); wn=sum('regulated-warn' in lint_v2(s) for s in HELD_OK); bb=rec(lint_v2,BENIGN)
print(f"v2 HELD-OUT prohibited recall: {hr}/{n} = {hr/n:.2f}; allowed blocked {fb}/{len(HELD_OK)} (warned {wn}); benign ad lines blocked {bb}/22")
print("missed:",[s for s in HELD_PROH if not block(lint_v2,s)])
ok = hr/n<0.5 and fb==0 and bb==0
print(("RESULT: PASS " if ok else "RESULT: FAIL ")+f"regex claims lint recall on TikTok's own unseen prohibited examples {hr}/{n} ({hr/n:.0%}), v1 rule-text-only {rec(lint_v1,TRAIN_PROH)}/14, false blocks {fb}/9 allowed and {bb}/22 benign")
