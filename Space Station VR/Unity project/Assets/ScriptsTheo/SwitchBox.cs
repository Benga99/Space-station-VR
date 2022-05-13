using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SwitchBox : MonoBehaviour
{
    [SerializeField]
    private GameObject doorInteractable;
    [SerializeField]
    private GameObject doorStatic;

    public void SetActiveDoorInteractable()
    {
        doorInteractable.SetActive(true);
        doorStatic.SetActive(false);
    }
}
