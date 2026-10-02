using UnityEngine;

// Test helper: press 1-8 to switch the pet's animation.
// The numbers match the "Mood" parameter in the Pup animator.
[RequireComponent(typeof(Animator))]
public class PetDemo : MonoBehaviour
{
    static readonly string[] Moods =
        { "idle", "happy", "sad", "crying", "eating", "playing", "studying", "sleeping" };

    Animator anim;

    void Awake() => anim = GetComponent<Animator>();

    void Update()
    {
        for (int i = 0; i < Moods.Length; i++)
            if (Input.GetKeyDown(KeyCode.Alpha1 + i))
                anim.SetInteger("Mood", i);
    }

    void OnGUI()
    {
        GUI.Label(new Rect(12, 10, 500, 24),
                  $"{Moods[anim.GetInteger("Mood")]}   (press 1-8 to change)");
    }
}
