using UnityEngine;

// The buttons call Play(mood). The pup plays that animation, then goes back
// to idle after a few seconds. Mood numbers match the Pup animator:
// 0 idle, 1 happy, 2 sad, 3 crying, 4 eating, 5 playing, 6 studying, 7 sleeping.
public class PetButtons : MonoBehaviour
{
    public Animator pet;
    public float seconds = 3f;

    public void Play(int mood)
    {
        pet.SetInteger("Mood", mood);
        CancelInvoke(nameof(BackToIdle));          // a second press restarts the timer
        Invoke(nameof(BackToIdle), seconds);
    }

    void BackToIdle() => pet.SetInteger("Mood", 0);
}
