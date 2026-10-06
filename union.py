def unir(co2, pib, vida):
    """Conserva los países y años que coinciden en las tres fuentes."""
    claves = ["Entity", "Code", "Year"]
    unidos = co2.merge(pib, on=claves, how="inner", validate="one_to_one")
    return unidos.merge(vida, on=claves, how="inner", validate="one_to_one")
