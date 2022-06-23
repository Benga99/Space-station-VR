using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SwitchBoxLevel3 : MonoBehaviour
{
    [SerializeField]
    private List<OperateSwitchButton> buttons;
    [SerializeField]
    private GameObject key;

    //it is on the interactable door

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("switch + " + this.gameObject.name);
    }

    // Update is called once per frame
    void Update()
    {
        if (buttons[0].isUp == true && buttons[1].isUp == false && buttons[2].isUp == true && buttons[3].isUp == true)
        {
            //open Door
            key.SetActive(true);
        }
    }
}
