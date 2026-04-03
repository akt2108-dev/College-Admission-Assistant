def build_category(base, girl=False, ph=False, af=False, ff=False, tf=False):
    base = base.strip().upper()

    if ph:
        return f"{base}(PH)"
    if af:
        return f"{base}(AF)"
    if ff:
        return f"{base}(FF)"
    if tf:
        return f"{base}(TF)"
    if girl:
        return f"{base}(GIRL)"

    return base