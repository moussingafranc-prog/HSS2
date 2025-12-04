import pygame
import random
import time
import csv
import os

# ==============================
# Paramètres généraux
# ==============================
SCREEN_W = 1200
SCREEN_H = 600
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)

BASE_FONT_SIZE = 80      # taille de base
DELTA_SIZE = 10          # différence de taille dans la condition "différente"
DEFAULT_N_TRIALS = 80    # valeur par défaut si l'utilisateur ne choisit rien

RESULTS_FILE = "exp_lettres_pygame.csv"

# Lettres et pseudo-lettres (à adapter si tu veux)
LETTERS = ["A", "E", "H", "M", "N", "R", "T"]
PSEUDO_LETTERS = ["@", "#", "&", "%", "§", "£", "¤"]


# ==============================
# Fonctions utilitaires
# ==============================

def draw_stimulus(surface, text, font, center, stim_type):
    """
    Dessine un stimulus au centre 'center'.

    stim_type:
      - "letter"  : lettre normale
      - "pseudo"  : pseudo-lettre normale
      - "mirror"  : lettre miroir (flip vertical : haut <-> bas)
    """
    img = font.render(text, True, TEXT_COLOR)

    # Lettre-miroir : symétrie verticale (haut-bas)
    if stim_type == "mirror":
        img = pygame.transform.flip(img, False, True)

    rect = img.get_rect(center=center)
    surface.blit(img, rect)
    return rect


def show_message(screen, clock, lines, font, wait_key=True):
    """
    Affiche un écran de message (instructions, pause, etc.).
    """
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                if wait_key:
                    running = False

        screen.fill(BG_COLOR)
        y = SCREEN_H // 2 - 40 * len(lines) // 2
        for line in lines:
            img = font.render(line, True, TEXT_COLOR)
            rect = img.get_rect(center=(SCREEN_W // 2, y))
            screen.blit(img, rect)
            y += 50

        pygame.display.flip()
        clock.tick(60)


def build_trials(n_trials):
    """
    Construit une liste d'essais.

    Chaque essai :
      - 'letter'        : lettre utilisée
      - 'pseudo'        : pseudo-lettre (utile pour comparaison pseudo)
      - 'lexical_side'  : 'left' ou 'right' (côté où apparaît la lettre)
      - 'relation'      : 'same', 'lex_smaller', 'lex_larger'
      - 'comparison'    : 'pseudo' ou 'mirror'
                          -> lettre vs pseudo-lettre ou lettre vs lettre-miroir
    """
    trials = []
    for _ in range(n_trials):
        letter = random.choice(LETTERS)
        pseudo = random.choice(PSEUDO_LETTERS)

        lexical_side = random.choice(["left", "right"])
        relation = random.choice(["same", "lex_smaller", "lex_larger"])
        comparison = random.choice(["pseudo", "mirror"])

        trials.append({
            "letter": letter,
            "pseudo": pseudo,
            "lexical_side": lexical_side,
            "relation": relation,
            "comparison": comparison,
        })

    random.shuffle(trials)
    return trials


# ==============================
# Boucle principale d'expérience
# ==============================

def run_experiment():
    # Demande nombre d'essais
    try:
        user_val = input(
            f"Nombre d'essais (ENTER pour {DEFAULT_N_TRIALS}) : "
        )
        if user_val.strip():
            n_trials = int(user_val)
        else:
            n_trials = DEFAULT_N_TRIALS
    except Exception:
        n_trials = DEFAULT_N_TRIALS

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Illusion de hauteur - Lettres")
    clock = pygame.time.Clock()

    font_instr = pygame.font.SysFont("Arial", 28)

    # Instructions
    show_message(
        screen,
        clock,
        [
            "Tâche : juger la hauteur de deux stimuli.",
            "Comparaisons : lettre vs pseudo-lettre, lettre vs lettre-miroir.",
            "F = stimulus gauche plus haut",
            "J = stimulus droite plus haut",
            "Barre espace = mêmes tailles",
            "Q = arrêter (sauvegarde des essais déjà réalisés)",
            "ESC = quitter immédiatement (sans sauvegarde)",
            "Appuie sur une touche pour commencer.",
        ],
        font_instr,
        wait_key=True,
    )

    trials = build_trials(n_trials)
    results = []

    center_left = (SCREEN_W // 4, SCREEN_H // 2)
    center_right = (3 * SCREEN_W // 4, SCREEN_H // 2)

    early_stop = False

    for idx, tr in enumerate(trials, start=1):
        if early_stop:
            break

        letter = tr["letter"]
        pseudo = tr["pseudo"]
        lexical_side = tr["lexical_side"]
        relation = tr["relation"]
        comparison = tr["comparison"]  # 'pseudo' ou 'mirror'

        # ITI
        iti_start = time.time()
        while time.time() - iti_start < 0.4 and not early_stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    early_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                    elif event.key == pygame.K_q:
                        early_stop = True

            screen.fill(BG_COLOR)
            pygame.display.flip()
            clock.tick(60)

        if early_stop:
            break

        # Tailles physiques selon la relation
        if relation == "same":
            size_letter = BASE_FONT_SIZE
            size_other = BASE_FONT_SIZE
        elif relation == "lex_smaller":
            size_letter = BASE_FONT_SIZE - DELTA_SIZE
            size_other = BASE_FONT_SIZE
        elif relation == "lex_larger":
            size_letter = BASE_FONT_SIZE + DELTA_SIZE
            size_other = BASE_FONT_SIZE
        else:
            size_letter = BASE_FONT_SIZE
            size_other = BASE_FONT_SIZE

        font_letter = pygame.font.SysFont("Arial", size_letter)
        font_other = pygame.font.SysFont("Arial", size_other)

        # Attribution gauche/droite selon lexical_side et comparison
        if lexical_side == "left":
            left_text = letter
            left_type = "letter"
            left_font = font_letter
            left_phys_size = size_letter

            if comparison == "pseudo":
                right_text = pseudo
                right_type = "pseudo"
            else:  # "mirror"
                right_text = letter
                right_type = "mirror"

            right_font = font_other
            right_phys_size = size_other

        else:  # lettre à droite
            right_text = letter
            right_type = "letter"
            right_font = font_letter
            right_phys_size = size_letter

            if comparison == "pseudo":
                left_text = pseudo
                left_type = "pseudo"
            else:  # "mirror"
                left_text = letter
                left_type = "mirror"

            left_font = font_other
            left_phys_size = size_other

        # Stimulus physiquement plus haut
        if left_phys_size > right_phys_size:
            true_larger = "left"
        elif right_phys_size > left_phys_size:
            true_larger = "right"
        else:
            true_larger = "equal"

        # Présentation + réponse
        response = None
        rt_ms = None
        t0 = time.time()
        trial_running = True

        while trial_running and not early_stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    early_stop = True
                    trial_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                    elif event.key == pygame.K_q:
                        early_stop = True
                        trial_running = False
                    elif event.key == pygame.K_f:
                        response = "left"
                        rt_ms = (time.time() - t0) * 1000.0
                        trial_running = False
                    elif event.key == pygame.K_j:
                        response = "right"
                        rt_ms = (time.time() - t0) * 1000.0
                        trial_running = False
                    elif event.key == pygame.K_SPACE:
                        response = "equal"
                        rt_ms = (time.time() - t0) * 1000.0
                        trial_running = False

            if early_stop:
                break

            screen.fill(BG_COLOR)

            info = (
                f"Essai {idx}/{n_trials}  "
                "(F=gauche, J=droite, ESPACE=même, Q=stop)"
            )
            img_info = font_instr.render(info, True, TEXT_COLOR)
            screen.blit(img_info, (20, 20))

            draw_stimulus(screen, left_text, left_font, center_left, left_type)
            draw_stimulus(screen, right_text, right_font, center_right, right_type)

            pygame.display.flip()
            clock.tick(60)

        if early_stop:
            break

        # Côté lexical choisi
        lexical_choice = None
        if response is not None:
            if response == "left" and lexical_side == "left":
                lexical_choice = "lexical"
            elif response == "right" and lexical_side == "right":
                lexical_choice = "lexical"
            elif response in ("left", "right"):
                lexical_choice = "non_lexical"
            else:
                lexical_choice = "equal"

        # Erreur
        if true_larger == "equal":
            is_error = int(response != "equal")
        else:
            is_error = int(response != true_larger)

        results.append({
            "trial": idx,
            "letter": letter,
            "pseudo": pseudo,
            "lexical_side": lexical_side,
            "relation": relation,
            "comparison": comparison,   # pseudo vs mirror
            "left_text": left_text,
            "right_text": right_text,
            "left_type": left_type,     # letter / pseudo / mirror
            "right_type": right_type,
            "left_phys_size": left_phys_size,
            "right_phys_size": right_phys_size,
            "true_larger": true_larger,
            "response": response,
            "lexical_choice": lexical_choice,
            "rt_ms": rt_ms if rt_ms is not None else "",
            "is_error": is_error,
        })

    pygame.quit()

    if not results:
        print("Aucun essai complété, aucun fichier sauvegardé.")
        return

    # Sauvegarde CSV
    fieldnames = list(results[0].keys())
    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print("Expérience terminée (ou arrêt anticipé).")
    print("Nombre d'essais enregistrés :", len(results))
    print("Résultats sauvegardés dans :", os.path.abspath(RESULTS_FILE))

    # Stat global
    total_n = len(results)
    total_err = sum(row["is_error"] for row in results)
    total_err_rate = total_err / total_n if total_n > 0 else 0.0

    print("\nTaux d'erreur global : "
          f"{total_err} erreurs sur {total_n} essais "
          f"({total_err_rate*100:.1f} %)")

    # Stat par (relation, true_larger, comparison)
    stats = {}

    for row in results:
        key = (row["relation"], row["true_larger"], row["comparison"])
        if key not in stats:
            stats[key] = {"n": 0, "n_err": 0}
        stats[key]["n"] += 1
        stats[key]["n_err"] += row["is_error"]

    print("\nStatistiques d'erreurs par (relation, true_larger, comparison) :")
    for key, val in sorted(stats.items()):
        relation, true_larger, comparison = key
        n = val["n"]
        n_err = val["n_err"]
        err_rate = n_err / n if n > 0 else 0.0
        print(
            f"  relation={relation:11s} | true_larger={true_larger:5s} "
            f"| comp={comparison:6s} | n={n:4d} | err={n_err:4d} "
            f"| taux={err_rate*100:5.1f} %"
        )


if __name__ == "__main__":
    run_experiment()
