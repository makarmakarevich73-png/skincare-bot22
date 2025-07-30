import re

soft_surfs = [
    "coco-glucoside", "lauryl glucoside", "decyl glucoside", "caprylyl/capryl glucoside",
    "disodium cocoamphodiacetate", "cocamidopropyl betaine", "sodium cocoyl glutamate",
    "sodium lauroyl glutamate", "sodium lauroyl methyl isethionate", "sodium methyl cocoyl taurate",
    "sodium cocoyl isethionate", "sodium lauryl glucose carboxylate", "lauryl hydroxysultaine",
    "laureth-6 carboxylic acid", "disodium lauroamphodiacetate", "sodium lauriminodipropionate",
    "sodium lauroyl oat amino acids", "potassium cocoyl hydrolyzed collagen",
    "potassium cocoyl glycinate", "disodium lauryl sulfosuccinate", "disodium oleamido mipa-sulfosuccinate",
    "lauryl glucoside citrate", "cocoamphodiacetate", "lauryl betaine", "sodium lauroyl sarcosinate",
    "sodium cocoyl sarcosinate", "sodium stearoyl glutamate", "cocoyl proline", "capryloyl glycine",
    "cocamidopropyl hydroxysultaine", "decyl polyglucose"
]

hard_surfs = [
    "sodium lauryl sulfate", "sodium laureth sulfate", "ammonium lauryl sulfate",
    "ammonium laureth sulfate", "cocamide dea", "cocamide mea", "peg-7 glyceryl cocoate",
    "sodium c14-16 olefin sulfonate", "sodium myreth sulfate", "sodium pareth sulfate",
    "sodium c12-14 pareth sulfate", "sodium laureth-8 sulfate", "ammonium xylenesulfonate",
    "sodium xylene sulfonate", "lauramide dea", "laureth-3", "laureth-4", "laureth-7",
    "sodium tallowate", "sodium palm kernelate", "sodium cocoate", "sodium palmate",
    "sodium ricinoleate", "triethanolamine lauryl sulfate", "tea-lauryl sulfate",
    "sodium dodecylbenzene sulfonate", "sodium cetyl sulfate", "sodium deceth sulfate",
    "sodium trideceth sulfate"
]

silicones = [
    "dimethicone", "cyclopentasiloxane", "cyclohexasiloxane", "amodimethicone",
    "trimethicone", "methicone", "phenyl trimethicone", "dimethiconol", "silicone quaterniums"
]

peg_40 = "peg-40"
bad_alcohols = ["alcohol", "ethanol"]
allowed_alcohols = ["cetyl alcohol", "cetearyl alcohol", "stearyl alcohol", "behenyl alcohol"]
oils_and_butters = ["oil", "butter"]

def normalize(ingredient):
    return ingredient.lower().strip()

def contains_any(ingredients, keywords):
    return any(any(k in i for k in keywords) for i in ingredients)

def count_matches(ingredients, keywords):
    return sum(any(k in i for k in keywords) for i in ingredients)

def analyze_surfactants(ingredients, skin_type):
    soft_count = count_matches(ingredients, soft_surfs)
    hard_count = count_matches(ingredients, hard_surfs)

    if skin_type in ["сухая", "чувствительная", "нормальная", "зрелая"]:
        if soft_count == 0:
            return "🟥 Умывалка слишком агрессивная — мягкие ПАВы не найдены."
        if soft_count <= 3:
            return "🟩 Подходит для утреннего очищения."
        if 4 <= soft_count <= 7:
            return "🟨 Подходит для вечернего очищения."
        return "🟥 Слишком много ПАВов — может пересушивать кожу."

    if skin_type in ["жирная", "комбинированная"]:
        result = []
        if hard_count == 0 and 3 <= soft_count <= 7:
            result.append("🟩 Подходит для утреннего очищения.")
        if hard_count == 1 and 2 <= soft_count <= 4:
            result.append("🟩 Подходит для вечернего очищения.")
        if not result:
            return "🟥 Неоптимальный состав: не соответствует рекомендациям для жирной/комби-кожи."
        return "\n".join(result)

    return "⚠️ Не удалось определить пригодность умывалки."

def analyze_toner(ingredients):
    top5 = ingredients[:5]
    has_bad_alcohol = any(a in ing for ing in top5 for a in bad_alcohols)
    has_peg_40 = any(peg_40 in ing for ing in top5)
    has_oil = any("oil" in ing or "butter" in ing for ing in top5)

    if has_bad_alcohol or has_peg_40 or has_oil:
        return "🟥 Нежелательные компоненты в топ-5. Тоник может сушить или перегружать кожу."
    return "🟩 Тоник выглядит безопасным по первым 5 компонентам."

def analyze_cream(ingredients, skin_type):
    top10 = ingredients[:10]
    top10_norm = [normalize(i) for i in top10]

    has_alcohol = (any(a in ing for ing in top10_norm for a in bad_alcohols)
                   and not any(aa in ing for ing in top10_norm for aa in allowed_alcohols))
    has_peg_40 = any(peg_40 in i for i in top10_norm)
    silicone_count = sum(1 for s in silicones if s in top10_norm)
    first5 = top10_norm[:5]

    has_algae = any("algae" in ing for ing in top10_norm)
    has_mint = any("mentha" in ing for ing in top10_norm)
    has_tea_tree = any("tea tree" in ing for ing in top10_norm)

    if skin_type in ["сухая", "чувствительная"]:
        if has_alcohol or has_algae or has_mint or has_tea_tree:
            return "🟥 Не подходит: содержит спирты, водоросли, мяту или чайное дерево."
        if has_peg_40:
            return "🟥 Не подходит: PEG-40 в топ-10."
        if silicone_count > 1 and any(s in f for s in silicones for f in first5):
            return "🟥 Слишком много силиконов в топ-5."
        return "🟩 Подходит для сухой/чувствительной кожи."

    if skin_type in ["комбинированная", "жирная"]:
        if has_alcohol or has_peg_40:
            return "🟥 Нежелательные компоненты (спирт или PEG-40)."
        if silicone_count > 1 or (any(s in f for s in silicones if s != "dimethicone" for f in first5)):
            return "🟥 Слишком много силиконов, особенно в топ-5."
        return "🟩 Подходит для жирной/комбинированной кожи."

    if skin_type == "нормальная":
        if has_alcohol or any(peg_40 in f for f in first5) or silicone_count > 1:
            return "🟨 Есть нежелательные компоненты в топ-5 — возможны реакции."
        return "🟩 Подходит для нормальной кожи."

    return "⚠️ Не удалось определить пригодность крема."

def analyze_product(ingredients_list, product_type, skin_type=None):
    ingredients = [normalize(i) for i in ingredients_list]

    if product_type == "умывалка":
        return analyze_surfactants(ingredients, skin_type)
    elif product_type == "тоник":
        return analyze_toner(ingredients)
    elif product_type == "крем":
        return analyze_cream(ingredients, skin_type)
    else:
        return "❓ Неизвестный тип продукта."
