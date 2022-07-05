using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SwitchBox : MonoBehaviour
{
    [SerializeField]
    private GameObject doorInteractable;
    [SerializeField]
    private GameObject doorStatic;
    [SerializeField]
    private GameObject remoteControl;

    public void SetActiveDoorInteractable()
    {
        doorInteractable.SetActive(true);
        doorStatic.SetActive(false);
        remoteControl.SetActive(true);
    }
}
