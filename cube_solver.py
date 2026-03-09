import argparse
import sys
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Face(Enum):
    """Enumeration of cube faces with their standard notation."""

    FRONT = "F"
    BACK = "B"
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class Color(Enum):
    """Enumeration of valid cube colors."""

    WHITE = "W"
    YELLOW = "Y"
    RED = "R"
    ORANGE = "O"
    BLUE = "B"
    GREEN = "G"


# Turkish translation mapping for moves and faces
TURKISH_MOVES: Dict[str, str] = {
    "F": "Ön yüzü saat yönünde 90° çevirin.",
    "F'": "Ön yüzü saat yönünün tersinde 90° çevirin.",
    "F2": "Ön yüzü 180° çevirin.",
    "B": "Arka yüzü saat yönünde 90° çevirin.",
    "B'": "Arka yüzü saat yönünün tersine 90° çevirin.",
    "B2": "Arka yüzü 180° çevirin.",
    "L": "Sol yüzü saat yönünde 90° çevirin.",
    "L'": "Sol yüzü saat yönünün tersinde 90° çevirin.",
    "L2": "Sol yüzü 180° çevirin.",
    "R": "Sağ yüzü saat yönünde 90° çevirin.",
    "R'": "Sağ yüzü saat yönünün tersinde 90° çevirin.",
    "R2": "Sağ yüzü 180° çevirin.",
    "U": "Üst yüzü saat yönünde 90° çevirin.",
    "U'": "Üst yüzü saat yönünün tersinde 90° çevirin.",
    "U2": "Üst yüzü 180° çevirin.",
    "D": "Alt yüzü saat yönünde 90° çevirin.",
    "D'": "Alt yüzü saat yönünün tersinde 90° çevirin.",
    "D2": "Alt yüzü 180° çevirin.",
}


def validate_face_input(face_str: str, face_name: str) -> bool:
    """
    Validate a single face input string.

    Args:
        face_str: String representing the face (9 characters).
        face_name: Name of the face for error reporting.

    Returns:
        True if valid, False otherwise.

    Raises:
        ValueError: If the face string is invalid.
    """
    if not face_str:
        raise ValueError(f"{face_name} yüzü belirtilmemiş.")

    if len(face_str) != 9:
        raise ValueError(
            f"{face_name} yüzü 9 karakter olmalıdır (3x3 grid). "
            f"Girilen: {len(face_str)} karakter."
        )

    valid_colors = {c.value for c in Color}
    for i, char in enumerate(face_str.upper()):
        if char not in valid_colors:
            raise ValueError(
                f"{face_name} yüzünde geçersiz renk: '{char}' (pozisyon: {i + 1}). "
                f"Geçerli renkler: {', '.join(sorted(valid_colors))}"
            )

    return True


def validate_cube_state(cube_state: Dict[str, str]) -> bool:
    """
    Validate the entire cube state for correctness.

    Args:
        cube_state: Dictionary mapping face names to their color strings.

    Returns:
        True if cube state is valid.

    Raises:
        ValueError: If the cube state is invalid.
    """
    # Check if all faces are present
    required_faces = {"front", "back", "left", "right", "top", "bottom"}
    provided_faces = set(cube_state.keys())

    if provided_faces != required_faces:
        missing = required_faces - provided_faces
        if missing:
            raise ValueError(f"Eksik yüzler: {', '.join(missing)}")

    # Validate each face
    face_name_map = {
        "front": "Ön",
        "back": "Arka",
        "left": "Sol",
        "right": "Sağ",
        "top": "Üst",
        "bottom": "Alt",
    }

    for face_key, face_str in cube_state.items():
        validate_face_input(face_str, face_name_map[face_key])

    # Count colors - each color should appear exactly 9 times
    color_counts: Dict[str, int] = {c.value: 0 for c in Color}

    for face_str in cube_state.values():
        for char in face_str.upper():
            color_counts[char] += 1

    for color, count in color_counts.items():
        if count != 9:
            raise ValueError(
                f"Renk sayısı hatası: '{color}' rengi {count} kez görünüyor "
                f"(olması gereken: 9). Her renk tam olarak 9 kez olmalıdır."
            )

    return True


def convert_to_kociemba_format(cube_state: Dict[str, str]) -> str:
    """
    Convert cube state to Kociemba algorithm format.

    Kociemba format: 54 characters representing the cube state.
    Order: U (top), R (right), F (front), D (bottom), L (left), B (back)
    Each face: 9 stickers in row-major order (top-left to bottom-right)

    Standard color scheme:
    - U (top) = White (W)
    - D (bottom) = Yellow (Y)
    - F (front) = Red (R)
    - B (back) = Orange (O)
    - L (left) = Green (G)
    - R (right) = Blue (B)

    Args:
        cube_state: Dictionary with face strings.

    Returns:
        String in Kociemba format (54 characters).
    """
    faces = [
        cube_state["top"],
        cube_state["right"],
        cube_state["front"],
        cube_state["bottom"],
        cube_state["left"],
        cube_state["back"],
    ]

    centers = {
        cube_state["top"][4]: "U",
        cube_state["right"][4]: "R",
        cube_state["front"][4]: "F",
        cube_state["bottom"][4]: "D",
        cube_state["left"][4]: "L",
        cube_state["back"][4]: "B",
    }

    cube_string = ""

    for face in faces:
        for sticker in face:
            cube_string += centers[sticker]

    return cube_string


def rotate_face_clockwise(face: List[str]) -> List[str]:
    """
    Rotate a face 90 degrees clockwise.

    Args:
        face: List of 9 elements representing a face.

    Returns:
        Rotated face as a list.
    """
    return [
        face[6],
        face[3],
        face[0],
        face[7],
        face[4],
        face[1],
        face[8],
        face[5],
        face[2],
    ]


def rotate_face_counterclockwise(face: List[str]) -> List[str]:
    """
    Rotate a face 90 degrees counterclockwise.

    Args:
        face: List of 9 elements representing a face.

    Returns:
        Rotated face as a list.
    """
    return [
        face[2],
        face[5],
        face[8],
        face[1],
        face[4],
        face[7],
        face[0],
        face[3],
        face[6],
    ]


def apply_move(cube: Dict[str, List[str]], move: str) -> Dict[str, List[str]]:
    """
    Apply a single move to the cube state.

    Args:
        cube: Current cube state as a dictionary of face lists.
        move: Move notation (e.g., 'R', 'U'', 'F2').

    Returns:
        Updated cube state.
    """
    # Create a deep copy to avoid modifying the original
    new_cube = {k: v[:] for k, v in cube.items()}

    base_move = move.rstrip("'2")
    is_prime = "'" in move
    is_double = "2" in move

    # Apply the base move
    if base_move == "R":
        # Rotate right face
        new_cube["R"] = rotate_face_clockwise(new_cube["R"])
        # Move edge pieces
        temp = [new_cube["U"][2], new_cube["U"][5], new_cube["U"][8]]
        new_cube["U"][2], new_cube["U"][5], new_cube["U"][8] = (
            new_cube["F"][2],
            new_cube["F"][5],
            new_cube["F"][8],
        )
        new_cube["F"][2], new_cube["F"][5], new_cube["F"][8] = (
            new_cube["D"][2],
            new_cube["D"][5],
            new_cube["D"][8],
        )
        new_cube["D"][2], new_cube["D"][5], new_cube["D"][8] = (
            new_cube["B"][6],
            new_cube["B"][3],
            new_cube["B"][0],
        )
        new_cube["B"][6], new_cube["B"][3], new_cube["B"][0] = temp

    elif base_move == "L":
        # Rotate left face
        new_cube["L"] = rotate_face_clockwise(new_cube["L"])
        # Move edge pieces
        temp = [new_cube["U"][0], new_cube["U"][3], new_cube["U"][6]]
        new_cube["U"][0], new_cube["U"][3], new_cube["U"][6] = (
            new_cube["B"][8],
            new_cube["B"][5],
            new_cube["B"][2],
        )
        new_cube["B"][8], new_cube["B"][5], new_cube["B"][2] = (
            new_cube["D"][0],
            new_cube["D"][3],
            new_cube["D"][6],
        )
        new_cube["D"][0], new_cube["D"][3], new_cube["D"][6] = (
            new_cube["F"][0],
            new_cube["F"][3],
            new_cube["F"][6],
        )
        new_cube["F"][0], new_cube["F"][3], new_cube["F"][6] = temp

    elif base_move == "U":
        # Rotate up face
        new_cube["U"] = rotate_face_clockwise(new_cube["U"])
        # Move edge pieces
        temp = [new_cube["F"][0], new_cube["F"][1], new_cube["F"][2]]
        new_cube["F"][0], new_cube["F"][1], new_cube["F"][2] = (
            new_cube["R"][0],
            new_cube["R"][1],
            new_cube["R"][2],
        )
        new_cube["R"][0], new_cube["R"][1], new_cube["R"][2] = (
            new_cube["B"][0],
            new_cube["B"][1],
            new_cube["B"][2],
        )
        new_cube["B"][0], new_cube["B"][1], new_cube["B"][2] = (
            new_cube["L"][0],
            new_cube["L"][1],
            new_cube["L"][2],
        )
        new_cube["L"][0], new_cube["L"][1], new_cube["L"][2] = temp

    elif base_move == "D":
        # Rotate down face
        new_cube["D"] = rotate_face_clockwise(new_cube["D"])
        # Move edge pieces
        temp = [new_cube["F"][6], new_cube["F"][7], new_cube["F"][8]]
        new_cube["F"][6], new_cube["F"][7], new_cube["F"][8] = (
            new_cube["L"][6],
            new_cube["L"][7],
            new_cube["L"][8],
        )
        new_cube["L"][6], new_cube["L"][7], new_cube["L"][8] = (
            new_cube["B"][6],
            new_cube["B"][7],
            new_cube["B"][8],
        )
        new_cube["B"][6], new_cube["B"][7], new_cube["B"][8] = (
            new_cube["R"][6],
            new_cube["R"][7],
            new_cube["R"][8],
        )
        new_cube["R"][6], new_cube["R"][7], new_cube["R"][8] = temp

    elif base_move == "F":
        # Rotate front face
        new_cube["F"] = rotate_face_clockwise(new_cube["F"])
        # Move edge pieces
        temp = [new_cube["U"][6], new_cube["U"][7], new_cube["U"][8]]
        new_cube["U"][6], new_cube["U"][7], new_cube["U"][8] = (
            new_cube["L"][8],
            new_cube["L"][5],
            new_cube["L"][2],
        )
        new_cube["L"][8], new_cube["L"][5], new_cube["L"][2] = (
            new_cube["D"][2],
            new_cube["D"][1],
            new_cube["D"][0],
        )
        new_cube["D"][2], new_cube["D"][1], new_cube["D"][0] = (
            new_cube["R"][0],
            new_cube["R"][3],
            new_cube["R"][6],
        )
        new_cube["R"][0], new_cube["R"][3], new_cube["R"][6] = temp

    elif base_move == "B":
        # Rotate back face
        new_cube["B"] = rotate_face_clockwise(new_cube["B"])
        # Move edge pieces
        temp = [new_cube["U"][0], new_cube["U"][1], new_cube["U"][2]]
        new_cube["U"][0], new_cube["U"][1], new_cube["U"][2] = (
            new_cube["R"][2],
            new_cube["R"][5],
            new_cube["R"][8],
        )
        new_cube["R"][2], new_cube["R"][5], new_cube["R"][8] = (
            new_cube["D"][8],
            new_cube["D"][7],
            new_cube["D"][6],
        )
        new_cube["D"][8], new_cube["D"][7], new_cube["D"][6] = (
            new_cube["L"][6],
            new_cube["L"][3],
            new_cube["L"][0],
        )
        new_cube["L"][6], new_cube["L"][3], new_cube["L"][0] = temp

    # Apply prime (counterclockwise) move
    if is_prime:
        new_cube = apply_move(cube, base_move)
        new_cube = apply_move(new_cube, base_move)
        new_cube = apply_move(new_cube, base_move)

    # Apply double move
    elif is_double:
        new_cube = apply_move(cube, base_move)
        new_cube = apply_move(new_cube, base_move)

    return new_cube


def is_solved(cube_string: str) -> bool:
    """
    Check if the cube is in a solved state.

    Args:
        cube_string: Cube state in Kociemba format.

    Returns:
        True if solved, False otherwise.
    """
    # In a solved cube, each face should have all 9 stickers
    for i in range(0, 54, 9):
        face = cube_string[i : i + 9]
        if len(set(face)) != 1:
            return False

    return True


def solve_with_kociemba(cube_string: str) -> List[str]:
    """
    Solve the Rubik's Cube using the Kociemba library if available.

    Args:
        cube_string: Cube state in Kociemba format.

    Returns:
        List of moves to solve the cube..

    Raises:
        ImportError: If kociemba library is not installed.
    """
    try:
        import kociemba

        # Solve the cube
        solution = kociemba.solve(cube_string)

        # Split the solution string into individual moves
        moves = solution.split()

        return moves

    except ImportError:
        raise ImportError(
            "Kociemba kütüphanesi yüklü değil.\nYüklemek için: pip install kociemba"
        )

    except Exception as e:
        raise ValueError(f"Küp çözülürken hata oluştur: {str(e)}")


def print_solution_steps(moves: List[str]) -> None:
    """
    Print the solution steps in Turkish.

    Args:
        moves: List of moves in standard notation.
    """
    if not moves:
        print("\nKüp zaten çözülmüş durumda!")
        return

    print("\n" + "=" * 60)
    print("ÇÖZÜM ADIMLARI")
    print("=" * 60)
    print(f"\nToplam {len(moves)} adımda küp çözülecek:\n")

    for i, move in enumerate(moves, 1):
        if move in TURKISH_MOVES:
            print(f"Adım {i:2d}: {TURKISH_MOVES[move]}")
        else:
            print(f"Adım {i:2d}: {move} (bilinmeyen hareket)")

    print("\n" + "=" * 60)
    print("İyi şanslar!")
    print("=" * 60 + "\n")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="3x3 Rubik Küp Çözücü - Kociemba Algoritması",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örneği:
    python cube_solver.py \\
        --front RRRRRRRRR \\
        --back OOOOOOOOO \\
        --left GGGGGGGGG \\
        --right BBBBBBBBB \\
        --top WWWWWWWWW \\
        --bottom YYYYYYYYY

Renk Kodları:
    W = Beyaz (White) | Y = Sarı (Yellow)
    R = Kırmızı (Red) | O = Turuncu (Orange)
    B = Mavi (Blue)   | G = Yeşil (Green)
""",
    )

    parser.add_argument(
        "--front",
        "-f",
        type=str,
        required=True,
        help="Ön yüz (9 karakter: W/Y/R/O/B/G)",
    )

    parser.add_argument(
        "--back",
        "-b",
        type=str,
        required=True,
        help="Arka yüz (9 karakter: W/Y/R/O/B/G)",
    )

    parser.add_argument(
        "--left",
        "-l",
        type=str,
        required=True,
        help="Sol yüz (9 karakter: W/Y/R/O/B/G)",
    )

    parser.add_argument(
        "--right",
        "-r",
        type=str,
        required=True,
        help="Sağ yüz (9 karakter: W/Y/R/O/B/G)",
    )

    parser.add_argument(
        "--top",
        "-t",
        type=str,
        required=True,
        help="Üst yüz (9 karakter: W/Y/R/O/B/G)",
    )

    parser.add_argument(
        "--bottom",
        "-d",
        type=str,
        required=True,
        help="Alt yüz (9 karakter: W/Y/R/O/B/G)",
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the Rubik's Cube solver application.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Create cube state dictionary
        cube_state = {
            "front": args.front,
            "back": args.back,
            "left": args.left,
            "right": args.right,
            "top": args.top,
            "bottom": args.bottom,
        }

        # Validate the cube state
        print("\nKüp durumu doğrulanıyor...")
        validate_cube_state(cube_state)
        print("Küp durumu geçerli!\n")

        # Convert to Kociemba format
        cube_string = convert_to_kociemba_format(cube_state)

        # Check if already solved
        if is_solved(cube_string):
            print("Küp zaten çözülmüş durumda!")

        # Solve the cube
        print("Küp çözülüyor...")

        try:
            moves = solve_with_kociemba(cube_string)
        except ImportError as e:
            print(f"\n{e}")

        # Print solution steps
        print_solution_steps(moves)

        return 0

    except ValueError as e:
        print(f"\nHata: {e}\n", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\n\nİşlem kullanıcı tarafından iptal edildi.\n", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
