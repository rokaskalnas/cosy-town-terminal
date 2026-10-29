import random
import time

DAY_LENGTH = 20 * 60  # Each in-game day lasts 20 real minutes.

size = 5
grid = [[None for _ in range(size)] for _ in range(size)]
selected = None

materials = 30
population = 0
visitors = 0
day = 1
day_started = time.time()
last_update = day_started

word_materials = 1
word_progress = 1

buildings = {
    "house": {"cost": 5, "work": 5},
    "shop": {"cost": 15, "work": 8},
    "hotel": {"cost": 25, "work": 12},
    "park": {"cost": 20, "work": 10},
}


def count_buildings(kind):
    return sum(
        1 for row in grid for plot in row
        if plot and plot["done"] and plot["type"] == kind
    )


def has_park_and_hotel():
    return count_buildings("park") > 0 and count_buildings("hotel") > 0


def add_visitors():
    global visitors
    visitors = random.randint(3, 20)
    print(f"{visitors} temporary visitors arrived. Materials are boosted 1.5x!")


def start_new_day():
    global day, visitors
    day += 1
    visitors = random.randint(3, 20) if has_park_and_hotel() else 0
    print(f"\nDay {day} has started!")
    if visitors:
        print(f"{visitors} visitors arrived from your park and hotel!")


def update_time():
    global materials, last_update, day_started

    now = time.time()

    while last_update < now:
        next_day = day_started + DAY_LENGTH
        segment_end = min(now, next_day)
        seconds = segment_end - last_update

        houses = count_buildings("house")
        visitor_multiplier = 1.5 if visitors > 0 else 1.0
        materials += houses * 0.25 * seconds * visitor_multiplier
        last_update = segment_end

        if last_update >= next_day:
            day_started = next_day
            start_new_day()


def draw():
    update_time()
    remaining = max(0, int(DAY_LENGTH - (time.time() - day_started)))
    minutes, seconds = divmod(remaining, 60)

    print("\n" + "=" * 48)
    print(
        f"Day {day} | Materials: {materials:.1f} | "
        f"Residents: {population} | Visitors: {visitors}"
    )
    print(f"Next day in: {minutes:02}:{seconds:02}")
    print(f"Word rewards: +{word_materials} material, +{word_progress} progress")
    print("=" * 48)

    symbols = {
        "house": "H",
        "shop": "S",
        "hotel": "L",
        "park": "P",
    }

    for y, row in enumerate(grid):
        cells = []
        for x, plot in enumerate(row):
            if plot is None:
                cell = "."
            elif not plot["done"]:
                cell = "?"
            else:
                cell = symbols[plot["type"]]

            if selected == (x, y):
                cell = f"[{cell}]"
            else:
                cell = f" {cell} "
            cells.append(cell)

        print(f"{y}: " + " ".join(cells))

    print("    " + "  ".join(str(x) for x in range(size)))
    print(". empty | ? building | H house | S shop | L hotel | P park")
    print("Commands: select x y | build house/shop/hotel/park | upgrade | help | quit")


def select_plot(x, y):
    global selected
    if 0 <= x < size and 0 <= y < size:
        selected = (x, y)
        print(f"Selected plot ({x}, {y}).")
    else:
        print("That plot is outside the grid.")


def start_building(kind):
    global materials

    if selected is None:
        print("Select an empty plot first.")
        return
    if kind not in buildings:
        print("That building type doesn't exist.")
        return

    x, y = selected
    if grid[y][x] is not None:
        print("That plot is already occupied.")
        return
    if kind == "shop" and population < 10:
        print("Shops unlock at 10 permanent residents.")
        return
    if kind == "hotel" and population < 30:
        print("Hotels unlock at 30 permanent residents.")
        return
    if kind == "hotel" and count_buildings("shop") == 0:
        print("Build a shop before building a hotel.")
        return
    if kind == "park" and count_buildings("hotel") == 0:
        print("Build a hotel before building a park.")
        return

    cost = buildings[kind]["cost"]
    if materials < cost:
        print(f"You need {cost} materials to start a {kind}.")
        return

    materials -= cost
    grid[y][x] = {
        "type": kind,
        "work": 0,
        "needed": buildings[kind]["work"],
        "done": False,
    }
    print(f"{kind.title()} started. Type words to build it!")


def complete_building(plot):
    global population, size, grid

    plot["done"] = True
    kind = plot["type"]
    print(f"{kind.title()} complete!")

    if kind == "house":
        residents = random.randint(2, 6)
        population += residents
        print(f"{residents} residents moved in.")

    if kind == "park" and count_buildings("hotel") > 0 and visitors == 0:
        add_visitors()

    if population >= 50 and size == 5:
        size = 7
        for row in grid:
            row.extend([None, None])
        grid.extend([[None for _ in range(size)] for _ in range(2)])
        print("Your town reached 50 residents! The grid expanded to 7x7.")


def add_word(word):
    global materials

    if selected is None:
        print("Select a plot and start a building first.")
        return

    x, y = selected
    plot = grid[y][x]
    if plot is None or plot["done"]:
        print("There is nothing under construction on that plot.")
        return

    multiplier = 1.5 if visitors > 0 else 1.0
    earned = word_materials * multiplier
    progress = word_progress * multiplier
    materials += earned
    plot["work"] += progress

    print(
        f"'{word}' earned {earned:g} materials and added {progress:g} progress "
        f"({min(plot['work'], plot['needed']):g}/{plot['needed']})."
    )

    if plot["work"] >= plot["needed"]:
        complete_building(plot)


def upgrade_shop():
    global materials, word_materials, word_progress

    if selected is None:
        print("Select a completed shop first.")
        return

    x, y = selected
    plot = grid[y][x]
    if not plot or not plot["done"] or plot["type"] != "shop":
        print("Select a completed shop to buy an upgrade.")
        return

    cost = 20 * word_materials
    if materials < cost:
        print(f"The upgrade costs {cost} materials.")
        return

    materials -= cost
    word_materials += 1
    word_progress += 1
    print("Upgrade bought! Each word now earns more materials and progress.")


def show_help():
    print("""
select x y       Select a plot; coordinates start at 0.
build house      Houses are available from the start.
build shop       Unlocks at 10 residents; lets you buy upgrades.
build hotel      Unlocks at 30 residents, after you build a shop.
build park       Requires a hotel. Visitors boost materials by 1.5x.
upgrade          At a completed shop, improve word rewards.
<type words>     Earn materials and progress on the selected building.
quit             Leave the game.

Houses add 2-6 permanent residents and earn 0.25 materials per second.
The town expands from 5x5 to 7x7 at 50 permanent residents.
Each in-game day lasts 20 real minutes. Park visitors leave at day end.
""")


print("Welcome to your town!")
show_help()

while True:
    draw()
    command = input("> ").strip().lower()

    if command == "quit":
        print("Thanks for playing!")
        break
    elif command == "help":
        show_help()
    elif command == "upgrade":
        upgrade_shop()
    elif command.startswith("select "):
        parts = command.split()
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            select_plot(int(parts[1]), int(parts[2]))
        else:
            print("Use: select x y")
    elif command.startswith("build "):
        parts = command.split(maxsplit=1)
        if len(parts) == 2:
            start_building(parts[1])
        else:
            print("Use: build house, build shop, build hotel, or build park")
    elif command:
        for word in command.split():
            add_word(word)