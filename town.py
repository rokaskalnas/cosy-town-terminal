import random
import time

DAY_LENGTH = 20 * 60 # each in game day is 20irl mins

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

def start_new_day():
    global day, visitors
    day += 1
    visitors = random.randint(3, 20) if has_park_and_hotel() else 0
    print(f"\nDay {day} has started!")
    if visitors
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
            start_new_day():

def draw():
    update_time()
    remaining = max(0, int(DAY_LENGTH - (time.time() - day_started)))
    minutes, seconds = divmod(remaining, 60)

    print("\n" + "=" * 48)
    print(
        f"Day {day} | Materials: {materials:.1f} | "
        f"Residents: {population} | Vistors: {visitors}"
    )
    print(f"Next day in: {minutes:02}:{seconds:02}")
    print(f"Word rewards: +{word_materials} material, +{word_progress} progress")
    print("=" * 48)

    for y, row in enumerate(grid):
        cells = []
        for x, plot in enumerate(row):
            if plot is None:
                cell = "."
            elif not plot["done"]:
                cell = "?"
            else:
                cell = plot["type"][0].upper

            if selected == (x, y):
                cell = f"[{cell}]"
            else:
                cell = f" {cell} "
            cells.append(cell)

        print(f"{y}: " + " ".join(cells))


    print("    " + "  ".join(str(x) for x in range(size)))
    print(". empty | ? building | H house | S shop | H hotel* | P park")
    print("Commands: select x y | build house/shop/hotel/park | upgrade | help | quit")

def select_plot(x, y):